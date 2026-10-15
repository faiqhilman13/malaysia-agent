"""Append-only audit log, hash-chained per tenant.

Each event's hash covers the previous hash and the event's canonical JSON, so editing or deleting any
past event breaks every hash after it. `verify_chain` recomputes the chain.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import AuditEvent, Tenant, as_utc, utcnow
from .redaction import redact


def _event_hash(prev_hash: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256((prev_hash + canonical).encode()).hexdigest()


def _payload(event: AuditEvent) -> dict[str, Any]:
    occurred = as_utc(event.occurred_at)
    return {
        "tenant_id": event.tenant_id,
        "occurred_at": occurred.isoformat() if occurred else None,
        "actor": event.actor,
        "action": event.action,
        "resource_type": event.resource_type,
        "resource_id": event.resource_id,
        "outcome": event.outcome,
        "details": event.details,
    }


def record(
    session: Session,
    *,
    tenant_id: str,
    actor: str,
    action: str,
    outcome: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
    occurred_at: datetime | None = None,
) -> AuditEvent:
    # Lock the tenant row so concurrent writers extend the chain one at a time.
    tenant = session.scalars(select(Tenant).where(Tenant.id == tenant_id).with_for_update()).one()
    event = AuditEvent(
        tenant_id=tenant_id,
        occurred_at=(occurred_at or utcnow()).replace(microsecond=0),
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        details=redact(details or {}),
        prev_hash=tenant.audit_head,
        hash="",
    )
    event.hash = _event_hash(event.prev_hash, _payload(event))
    tenant.audit_head = event.hash
    session.add(event)
    session.flush()
    return event


def verify_chain(session: Session, tenant_id: str) -> dict[str, Any]:
    events = session.scalars(select(AuditEvent).where(AuditEvent.tenant_id == tenant_id).order_by(AuditEvent.id)).all()
    tenant = session.get(Tenant, tenant_id)
    expected_prev = "0" * 64
    for event in events:
        if event.prev_hash != expected_prev or event.hash != _event_hash(event.prev_hash, _payload(event)):
            return {"valid": False, "events": len(events), "first_bad_event_id": event.id}
        expected_prev = event.hash
    head_ok = tenant is not None and tenant.audit_head == expected_prev
    return {"valid": head_ok, "events": len(events), "head": expected_prev}


def export(session: Session, tenant_id: str, *, after_id: int = 0, limit: int = 200) -> list[dict[str, Any]]:
    events = session.scalars(
        select(AuditEvent)
        .where(AuditEvent.tenant_id == tenant_id, AuditEvent.id > after_id)
        .order_by(AuditEvent.id)
        .limit(limit)
    ).all()
    return [{"id": e.id, **_payload(e), "prev_hash": e.prev_hash, "hash": e.hash} for e in events]
