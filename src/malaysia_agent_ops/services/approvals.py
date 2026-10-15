"""Human approvals for legally binding actions.

Fixes every bypass the v0 audit found:
- Bound to one exact payload (hash). Changing the document voids the approval.
- Single use: consumed by the action it approved.
- Expiring.
- Decided only by a human: through a one-time link sent to the approver, or by an approver-role
  principal bound to a user. Never through an agent tool, and never by the principal that asked.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import Approval, Tenant, User, as_utc
from ..errors import Conflict, Forbidden, NotConfigured, NotFound
from ..security.auth import Principal
from . import audit
from .notify import ApprovalMessage, Notifier

State = Literal["approved", "pending", "rejected"]
ALWAYS_IN_PRODUCTION = {"einvoice.cancel", "einvoice.reject"}


@dataclass(frozen=True)
class ApprovalPolicy:
    """Per-tenant policy, stored in tenants.settings["approval_policy"]."""

    submit: bool = True
    cancel: bool = True
    reject: bool = True
    # Submit without approval when the payable amount is at or below this (None = always ask).
    auto_approve_submit_max: Decimal | None = None
    ttl_minutes: int = 24 * 60

    @classmethod
    def for_tenant(cls, tenant: Tenant, default_ttl: int) -> ApprovalPolicy:
        raw: dict[str, Any] = dict((tenant.settings or {}).get("approval_policy", {}))
        cap = raw.get("auto_approve_submit_max")
        return cls(
            submit=bool(raw.get("submit", True)),
            cancel=bool(raw.get("cancel", True)),
            reject=bool(raw.get("reject", True)),
            auto_approve_submit_max=Decimal(str(cap)) if cap is not None else None,
            ttl_minutes=int(raw.get("ttl_minutes", default_ttl)),
        )

    def requires(self, action: str, environment: str, amount: Decimal | None = None) -> bool:
        if environment == "production" and action in ALWAYS_IN_PRODUCTION:
            return True
        if action == "einvoice.submit":
            if not self.submit:
                return False
            return not (
                self.auto_approve_submit_max is not None
                and amount is not None
                and amount <= self.auto_approve_submit_max
            )
        return {"einvoice.cancel": self.cancel, "einvoice.reject": self.reject}.get(action, True)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class ApprovalService:
    def __init__(self, *, notifier: Notifier, public_base_url: str) -> None:
        self.notifier = notifier
        self.public_base_url = public_base_url.rstrip("/")

    # -- requesting -----------------------------------------------------------------------------

    def request_or_get(
        self,
        session: Session,
        *,
        tenant_id: str,
        action: str,
        resource_id: str,
        payload_hash: str,
        summary: dict[str, Any],
        requested_by: str,
        ttl_minutes: int,
        now: datetime,
    ) -> tuple[Approval, State]:
        """Return the live approval for this exact payload, creating and sending one if none exists."""
        existing = session.scalars(
            select(Approval)
            .where(
                Approval.tenant_id == tenant_id,
                Approval.action == action,
                Approval.resource_id == resource_id,
                Approval.payload_hash == payload_hash,
                Approval.status.in_(("pending", "approved", "rejected")),
            )
            .order_by(Approval.requested_at.desc())
        ).first()
        if existing is not None:
            if existing.status == "rejected":
                return existing, "rejected"
            if as_utc(existing.expires_at) > now:
                return existing, "approved" if existing.status == "approved" else "pending"

        approvers = session.scalars(
            select(User).where(User.tenant_id == tenant_id, User.role.in_(("approver", "admin")))
        ).all()
        if not approvers:
            raise NotConfigured(
                "No approver is set up for this account, so the action cannot be approved. "
                "Ask an admin to add a user with the approver role."
            )
        tokens = {user.id: secrets.token_urlsafe(32) for user in approvers}
        approval = Approval(
            tenant_id=tenant_id,
            action=action,
            resource_id=resource_id,
            payload_hash=payload_hash,
            summary=summary,
            requested_by=requested_by,
            requested_at=now,
            expires_at=now + timedelta(minutes=ttl_minutes),
            token_hashes={user_id: _hash(token) for user_id, token in tokens.items()},
        )
        session.add(approval)
        session.flush()
        for user in approvers:
            link = f"{self.public_base_url}/approve/{approval.id}?u={user.id}&t={tokens[user.id]}"
            self.notifier.send(
                ApprovalMessage(
                    user_id=user.id,
                    email=user.email,
                    phone=user.phone,
                    subject=f"Approve: {summary.get('title', action)}",
                    body=_describe(summary, approval),
                    link=link,
                )
            )
        audit.record(
            session,
            tenant_id=tenant_id,
            actor=requested_by,
            action="approval.requested",
            outcome="pending",
            resource_type="approval",
            resource_id=approval.id,
            details={"for_action": action, "resource_id": resource_id, "approvers": len(approvers)},
            occurred_at=now,
        )
        return approval, "pending"

    def consume(self, session: Session, approval: Approval, *, now: datetime) -> None:
        if approval.status != "approved":
            raise Conflict("Approval is not in an approved state.")
        approval.status = "consumed"
        approval.consumed_at = now

    # -- deciding (humans only) -----------------------------------------------------------------

    def get_for_link(self, session: Session, approval_id: str, user_id: str, token: str) -> Approval:
        approval = session.get(Approval, approval_id)
        expected = (approval.token_hashes or {}).get(user_id) if approval else None
        if approval is None or expected is None or not hmac.compare_digest(expected, _hash(token)):
            raise NotFound("Approval link is invalid.")
        return approval

    def decide_with_link(
        self,
        session: Session,
        *,
        approval_id: str,
        user_id: str,
        token: str,
        approve: bool,
        note: str | None,
        now: datetime,
    ) -> Approval:
        approval = self.get_for_link(session, approval_id, user_id, token)
        return self._decide(session, approval, decided_by=f"user:{user_id}", approve=approve, note=note, now=now)

    def decide_as_principal(
        self,
        session: Session,
        principal: Principal,
        *,
        approval_id: str,
        approve: bool,
        note: str | None,
        now: datetime,
    ) -> Approval:
        if principal.role not in ("approver", "admin") or principal.user_id is None:
            raise Forbidden("Only a human approver can decide approvals.")
        approval = session.get(Approval, approval_id)
        if approval is None or approval.tenant_id != principal.tenant_id:
            raise NotFound("Approval not found.")
        if approval.requested_by == principal.subject:
            raise Forbidden("The principal that requested an approval cannot decide it.")
        return self._decide(
            session, approval, decided_by=f"user:{principal.user_id}", approve=approve, note=note, now=now
        )

    def _decide(
        self, session: Session, approval: Approval, *, decided_by: str, approve: bool, note: str | None, now: datetime
    ) -> Approval:
        if approval.status != "pending":
            raise Conflict(f"Approval is already {approval.status}.")
        if as_utc(approval.expires_at) <= now:
            raise Conflict("Approval has expired. The agent must request it again.")
        approval.status = "approved" if approve else "rejected"
        approval.decided_by = decided_by
        approval.decided_at = now
        approval.decision_note = note
        approval.token_hashes = {}  # links are single use
        audit.record(
            session,
            tenant_id=approval.tenant_id,
            actor=decided_by,
            action="approval.decided",
            outcome=approval.status,
            resource_type="approval",
            resource_id=approval.id,
            details={"for_action": approval.action, "resource_id": approval.resource_id, "note": note},
            occurred_at=now,
        )
        return approval


def public_view(approval: Approval, now: datetime) -> dict[str, Any]:
    status = approval.status
    if status == "pending" and as_utc(approval.expires_at) <= now:
        status = "expired"
    return {
        "approval_id": approval.id,
        "action": approval.action,
        "resource_id": approval.resource_id,
        "status": status,
        "summary": approval.summary,
        "requested_at": as_utc(approval.requested_at).isoformat(),
        "expires_at": as_utc(approval.expires_at).isoformat(),
        "decided_at": as_utc(approval.decided_at).isoformat() if approval.decided_at else None,
        "decision_note": approval.decision_note,
    }


def _describe(summary: dict[str, Any], approval: Approval) -> str:
    lines = [summary.get("title", approval.action)]
    for key, value in summary.items():
        if key != "title":
            lines.append(f"{key.replace('_', ' ')}: {value}")
    lines.append(f"Expires: {as_utc(approval.expires_at).isoformat()}")
    return "\n".join(lines)
