"""The e-invoice workflows agents call, behind both the MCP tools and the REST API.

Every method checks the caller's tenant, the mandate (appointment and permission) for the taxpayer,
and the approval policy before anything reaches MyInvois. Every outcome is audited. Errors come back
as envelopes, never as raw exceptions, so agents always get a status and a next step.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Callable
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import Appointment, Approval, Credential, Document, Taxpayer, Tenant, as_utc
from ..envelope import envelope, error_envelope
from ..errors import Conflict, Forbidden, InvalidInput, NotConfigured, NotFound, OpsError, UpstreamError
from ..myinvois import codes
from ..myinvois.client import ClientCredentials
from ..myinvois.consolidation import Receipt
from ..myinvois.consolidation import plan as plan_consolidation
from ..myinvois.invoice import InvoiceInput, Party, compute_totals, is_valid_tin, normalise_tin
from ..myinvois.signing import SigningKey, sign_document, verify_document
from ..myinvois.ubl import build_document, serialize, sha256_hex, submission_entry
from ..runtime import ENVIRONMENTS, Runtime
from ..security.auth import Principal
from . import audit, idempotency
from .approvals import ApprovalPolicy, ApprovalService, public_view
from .redaction import mask_id

log = logging.getLogger("myops.einvoice")

SVDP_START = date(2026, 7, 7)
SVDP_END = date(2027, 12, 31)
TOOL_ROLES = ("agent", "admin")


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return as_utc(datetime.fromisoformat(str(value).replace("Z", "+00:00")))
    except ValueError:
        return None


def _flatten_errors(error: Any, prefix: str = "") -> list[str]:
    """Turn MyInvois's nested error objects into readable lines."""
    if isinstance(error, list):
        return [line for item in error for line in _flatten_errors(item, prefix)]
    if not isinstance(error, dict):
        return [f"{prefix}{error}"] if error else []
    lines: list[str] = []
    message = error.get("error") or error.get("message") or error.get("errorMs")
    target = error.get("propertyPath") or error.get("target") or error.get("propertyName")
    if message and not isinstance(message, (dict, list)):
        lines.append(f"{prefix}{target + ': ' if target else ''}{message}")
    for key in ("details", "innerError", "validationSteps", "error"):
        nested = error.get(key)
        if isinstance(nested, (dict, list)):
            lines.extend(_flatten_errors(nested, prefix))
    return lines


class EInvoiceService:
    def __init__(self, rt: Runtime) -> None:
        self.rt = rt
        self.approvals = ApprovalService(notifier=rt.notifier, public_base_url=rt.settings.public_base_url)

    # -- plumbing -------------------------------------------------------------------------------

    def _run(self, principal: Principal, action: str, fn: Callable[[Session], dict[str, Any]]) -> dict[str, Any]:
        if principal.role not in TOOL_ROLES:
            return error_envelope(Forbidden("Approver credentials cannot call agent tools."))
        try:
            with self.rt.db.session() as session:
                try:
                    with session.begin_nested():
                        return fn(session)
                except OpsError as exc:
                    audit.record(
                        session,
                        tenant_id=principal.tenant_id,
                        actor=principal.subject,
                        action=action,
                        outcome=exc.code,
                        details={"message": exc.message},
                        occurred_at=self.rt.clock(),
                    )
                    return error_envelope(exc)
        except Exception:
            log.exception("Unexpected error in %s", action)
            return envelope(
                "error",
                data={"error_code": "internal_error"},
                blocking_reason="Unexpected server error. It has been logged; nothing was changed.",
            )

    @staticmethod
    def _check_env(environment: str) -> None:
        if environment not in ENVIRONMENTS:
            raise InvalidInput("environment must be preprod or production")

    def _mandate(
        self, s: Session, principal: Principal, taxpayer_tin: str, permission: str | None, now: datetime
    ) -> tuple[Taxpayer, Appointment]:
        tin = normalise_tin(taxpayer_tin)
        taxpayer = s.scalar(select(Taxpayer).where(Taxpayer.tenant_id == principal.tenant_id, Taxpayer.tin == tin))
        if taxpayer is None:
            raise Forbidden(f"This account has no mandate to act for taxpayer {tin}.")
        appointments = s.scalars(
            select(Appointment).where(Appointment.taxpayer_id == taxpayer.id, Appointment.status == "active")
        ).all()
        current = [a for a in appointments if as_utc(a.valid_from) <= now <= as_utc(a.valid_to)]
        if not current:
            raise Forbidden(f"The appointment for taxpayer {tin} is missing, not yet valid, or expired.")
        if permission is None:
            return taxpayer, current[0]
        granted = [a for a in current if permission in a.permissions]
        if not granted:
            raise Forbidden(
                f"The appointment for taxpayer {tin} does not grant {permission}. The director must enable it in "
                "the MyInvois portal and an admin must update the mandate here."
            )
        return taxpayer, granted[0]

    def _credential(
        self, s: Session, tenant_id: str, taxpayer_id: str | None, kind: str, environment: str
    ) -> Credential | None:
        return s.scalar(
            select(Credential)
            .where(
                Credential.tenant_id == tenant_id,
                Credential.taxpayer_id.is_(None) if taxpayer_id is None else Credential.taxpayer_id == taxpayer_id,
                Credential.kind == kind,
                Credential.environment == environment,
            )
            .order_by(Credential.created_at.desc())
        )

    def _client_credentials(
        self, s: Session, taxpayer: Taxpayer, appointment: Appointment, environment: str
    ) -> tuple[ClientCredentials, str | None]:
        if appointment.mode == "intermediary":
            record = self._credential(s, taxpayer.tenant_id, None, "myinvois_client", environment)
            on_behalf_of: str | None = taxpayer.tin
        else:
            record = self._credential(s, taxpayer.tenant_id, taxpayer.id, "myinvois_client", environment)
            on_behalf_of = None
        if record is None:
            raise NotConfigured(
                f"No MyInvois {environment} Client ID is stored for this "
                f"{'account' if appointment.mode == 'intermediary' else 'taxpayer'}. An admin must add it."
            )
        secret = self.rt.vault.decrypt(record.ciphertext)
        return ClientCredentials(secret["client_id"], secret["client_secret"]), on_behalf_of

    def _signing_key(self, s: Session, taxpayer: Taxpayer, environment: str) -> SigningKey:
        record = self._credential(
            s, taxpayer.tenant_id, taxpayer.id, "signing_certificate", environment
        ) or self._credential(s, taxpayer.tenant_id, None, "signing_certificate", environment)
        if record is None:
            raise NotConfigured(f"Version 1.1 documents need a signing certificate; none is stored for {environment}.")
        return SigningKey.from_secret(self.rt.vault.decrypt(record.ciphertext))

    def _document(self, s: Session, principal: Principal, document_id: str) -> Document:
        doc = s.get(Document, document_id)
        if doc is None or doc.tenant_id != principal.tenant_id:
            raise NotFound("Document not found.")
        return doc

    def _view(self, doc: Document) -> dict[str, Any]:
        view: dict[str, Any] = {
            "document_id": doc.id,
            "environment": doc.environment,
            "document_type": codes.DOCUMENT_TYPES[doc.document_type],
            "version": doc.version,
            "code_number": doc.code_number,
            "status": doc.status,
            "buyer": {"tin": doc.buyer_tin, "name": doc.buyer_name},
            "currency": doc.currency,
            "payable_amount": str(doc.payable_amount),
            "issued_at": as_utc(doc.issued_at).isoformat(),
            "uuid": doc.uuid,
            "submission_uid": doc.submission_uid,
        }
        for field in ("submitted_at", "validated_at", "cancelled_at"):
            value = getattr(doc, field)
            if value:
                view[field] = as_utc(value).isoformat()
        if doc.status == "valid" and doc.uuid and doc.long_id:
            view["validation_link"] = f"{self.rt.portal_base(doc.environment)}/{doc.uuid}/share/{doc.long_id}"
        if doc.errors:
            view["errors"] = doc.errors
        return view

    def _audit(
        self, s: Session, principal: Principal, action: str, outcome: str, doc: Document | None = None, **details: Any
    ) -> None:
        audit.record(
            s,
            tenant_id=principal.tenant_id,
            actor=principal.subject,
            action=action,
            outcome=outcome,
            resource_type="document" if doc else None,
            resource_id=doc.id if doc else None,
            details=details,
            occurred_at=self.rt.clock(),
        )

    def _gate(
        self,
        s: Session,
        principal: Principal,
        *,
        action: str,
        environment: str,
        resource_id: str,
        payload_hash: str,
        summary: dict[str, Any],
        amount: Decimal | None,
        now: datetime,
    ) -> tuple[Approval | None, dict[str, Any] | None]:
        """Returns (approval to consume, None) to proceed, or (None, envelope) to stop and wait."""
        tenant = s.get(Tenant, principal.tenant_id)
        assert tenant is not None
        policy = ApprovalPolicy.for_tenant(tenant, self.rt.settings.approval_ttl_minutes)
        if not policy.requires(action, environment, amount):
            return None, None
        approval, state = self.approvals.request_or_get(
            s,
            tenant_id=principal.tenant_id,
            action=action,
            resource_id=resource_id,
            payload_hash=payload_hash,
            summary=summary,
            requested_by=principal.subject,
            ttl_minutes=policy.ttl_minutes,
            now=now,
        )
        if state == "approved":
            return approval, None
        if state == "rejected":
            return None, envelope(
                "blocked",
                data={"approval": public_view(approval, now)},
                blocking_reason="The approver rejected this request.",
                next_action="Change the request (a changed document needs a new approval) or stop.",
                resource_id=resource_id,
            )
        return None, envelope(
            "awaiting_human_approval",
            data={"approval": public_view(approval, now)},
            blocking_reason="A human approver must approve this exact request. They have been sent a link.",
            next_action=f"Check approval_get_status(approval_id='{approval.id}'); once approved, repeat this call.",
            resource_id=resource_id,
        )

    # -- read tools -----------------------------------------------------------------------------

    def list_taxpayers(self, principal: Principal) -> dict[str, Any]:
        def go(s: Session) -> dict[str, Any]:
            now = self.rt.clock()
            items = []
            for tp in s.scalars(
                select(Taxpayer).where(Taxpayer.tenant_id == principal.tenant_id).order_by(Taxpayer.name)
            ):
                appointments = s.scalars(select(Appointment).where(Appointment.taxpayer_id == tp.id)).all()
                active = [
                    a
                    for a in appointments
                    if a.status == "active" and as_utc(a.valid_from) <= now <= as_utc(a.valid_to)
                ]
                mode = active[0].mode if active else None
                readiness = {}
                for env in ENVIRONMENTS:
                    client = self._credential(
                        s, tp.tenant_id, None if mode == "intermediary" else tp.id, "myinvois_client", env
                    )
                    cert = self._credential(s, tp.tenant_id, tp.id, "signing_certificate", env) or self._credential(
                        s, tp.tenant_id, None, "signing_certificate", env
                    )
                    readiness[env] = {"myinvois_client": client is not None, "signing_certificate": cert is not None}
                items.append(
                    {
                        "tin": tp.tin,
                        "name": tp.name,
                        "mandate": {
                            "mode": mode,
                            "permissions": sorted({p for a in active for p in a.permissions}),
                            "valid_to": max((as_utc(a.valid_to) for a in active), default=None),
                        }
                        if active
                        else None,
                        "ready": readiness,
                    }
                )
            for item in items:
                if item["mandate"] and item["mandate"]["valid_to"]:
                    item["mandate"]["valid_to"] = item["mandate"]["valid_to"].isoformat()
            return envelope("success", data={"taxpayers": items})

        return self._run(principal, "taxpayers.list", go)

    def validate_counterparty(
        self, principal: Principal, *, taxpayer_tin: str, environment: str, tin: str, id_type: str, id_value: str
    ) -> dict[str, Any]:
        def go(s: Session) -> dict[str, Any]:
            self._check_env(environment)
            target = normalise_tin(tin)
            if not is_valid_tin(target):
                return envelope(
                    "invalid", data={"valid": False, "tin": target}, blocking_reason="TIN format is not valid."
                )
            if id_type not in codes.ID_TYPES:
                raise InvalidInput("id_type must be BRN, NRIC, PASSPORT or ARMY")
            taxpayer, appointment = self._mandate(s, principal, taxpayer_tin, None, self.rt.clock())
            creds, obo = self._client_credentials(s, taxpayer, appointment, environment)
            valid = self.rt.myinvois(environment).validate_tin(
                creds, obo, tin=target, id_type=id_type, id_value=id_value
            )
            self._audit(
                s, principal, "counterparty.validate", "valid" if valid else "not_found", tin=target, id_type=id_type
            )
            return envelope(
                "success",
                data={"valid": valid, "tin": target, "id_type": id_type, "id_value": mask_id(id_value)},
                next_action=None if valid else "Ask the counterparty to confirm their TIN and registration number.",
                source_system="myinvois",
            )

        return self._run(principal, "counterparty.validate", go)

    def search_counterparty_tin(
        self,
        principal: Principal,
        *,
        taxpayer_tin: str,
        environment: str,
        id_type: str | None = None,
        id_value: str | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        def go(s: Session) -> dict[str, Any]:
            self._check_env(environment)
            if not (id_type and id_value) and not name:
                raise InvalidInput("Give id_type and id_value, or a registered name.")
            taxpayer, appointment = self._mandate(s, principal, taxpayer_tin, None, self.rt.clock())
            creds, obo = self._client_credentials(s, taxpayer, appointment, environment)
            found = self.rt.myinvois(environment).search_tin(
                creds, obo, id_type=id_type, id_value=id_value, taxpayer_name=name
            )
            self._audit(s, principal, "counterparty.search_tin", "found" if found else "not_found")
            return envelope("success", data={"tin": found, "found": found is not None}, source_system="myinvois")

        return self._run(principal, "counterparty.search_tin", go)

    def get_document(self, principal: Principal, *, document_id: str) -> dict[str, Any]:
        def go(s: Session) -> dict[str, Any]:
            doc = self._document(s, principal, document_id)
            self._mandate(s, principal, s.get(Taxpayer, doc.taxpayer_id).tin, "view_documents", self.rt.clock())
            return envelope("success", data=self._view(doc), resource_id=doc.id)

        return self._run(principal, "einvoice.get", go)

    def list_documents(
        self, principal: Principal, *, taxpayer_tin: str | None = None, status: str | None = None, limit: int = 50
    ) -> dict[str, Any]:
        def go(s: Session) -> dict[str, Any]:
            query = select(Document).where(Document.tenant_id == principal.tenant_id)
            if taxpayer_tin:
                taxpayer, _ = self._mandate(s, principal, taxpayer_tin, "view_documents", self.rt.clock())
                query = query.where(Document.taxpayer_id == taxpayer.id)
            if status:
                query = query.where(Document.status == status)
            docs = s.scalars(query.order_by(Document.created_at.desc()).limit(max(1, min(limit, 200)))).all()
            return envelope("success", data={"documents": [self._view(d) for d in docs]})

        return self._run(principal, "einvoice.list", go)

    def approval_status(self, principal: Principal, *, approval_id: str) -> dict[str, Any]:
        def go(s: Session) -> dict[str, Any]:
            approval = s.get(Approval, approval_id)
            if approval is None or approval.tenant_id != principal.tenant_id:
                raise NotFound("Approval not found.")
            view = public_view(approval, self.rt.clock())
            next_action = {
                "approved": "Repeat the original call to carry out the approved action.",
                "pending": "Wait; the approver has not decided yet.",
                "expired": "Repeat the original call to request a new approval.",
            }.get(view["status"])
            return envelope("success", data=view, next_action=next_action, resource_id=approval.id)

        return self._run(principal, "approval.status", go)

    def audit_export(self, principal: Principal, *, after_id: int = 0, limit: int = 200) -> dict[str, Any]:
        def go(s: Session) -> dict[str, Any]:
            events = audit.export(s, principal.tenant_id, after_id=after_id, limit=max(1, min(limit, 1000)))
            return envelope("success", data={"chain": audit.verify_chain(s, principal.tenant_id), "events": events})

        return self._run(principal, "audit.export", go)

    # -- drafting -------------------------------------------------------------------------------

    def draft(
        self, principal: Principal, *, taxpayer_tin: str, environment: str, invoice: InvoiceInput
    ) -> dict[str, Any]:
        return self._run(
            principal, "einvoice.draft", lambda s: self._draft(s, principal, taxpayer_tin, environment, invoice)
        )

    def _draft(
        self, s: Session, principal: Principal, taxpayer_tin: str, environment: str, invoice: InvoiceInput
    ) -> dict[str, Any]:
        self._check_env(environment)
        now = self.rt.clock()
        taxpayer, _ = self._mandate(s, principal, taxpayer_tin, "submit_documents", now)
        role = "buyer" if invoice.is_self_billed else "supplier"
        if invoice.issuer_tin != taxpayer.tin:
            raise InvalidInput(f"{role}.tin must be {taxpayer.tin}, the taxpayer you are acting for.")
        version = codes.VERSIONS[invoice.version]
        if version["svdp"] and not SVDP_START <= now.date() <= SVDP_END:
            raise InvalidInput(f"SVDP versions are only accepted from {SVDP_START} to {SVDP_END}.")

        issued_at = invoice.issued_at or now
        totals = compute_totals(invoice)
        data = serialize(build_document(invoice, issued_at, totals))
        if len(data) > codes.MAX_DOCUMENT_BYTES:
            raise InvalidInput("The document is over MyInvois's 300 KB limit; split it into several invoices.")

        warnings: list[str] = []
        consolidated = any(line.classification_code == codes.CLASSIFICATION_CONSOLIDATED for line in invoice.lines)
        if consolidated and invoice.buyer.tin != codes.GENERAL_TIN_PUBLIC:
            raise InvalidInput(
                f"Consolidated e-invoices (classification 004) must use buyer TIN {codes.GENERAL_TIN_PUBLIC}."
            )
        if consolidated:
            big = [
                line.description
                for line, t in zip(invoice.lines, totals.lines, strict=True)
                if t.line_extension + t.tax > codes.CONSOLIDATION_LIMIT_MYR
            ]
            if big:
                warnings.append(
                    "Lines above RM10,000 in a consolidated e-invoice: if any is a single transaction it needs its own "
                    f"e-invoice instead ({', '.join(big[:5])})."
                )
        if version["signed"] and not (
            self._credential(s, taxpayer.tenant_id, taxpayer.id, "signing_certificate", environment)
            or self._credential(s, taxpayer.tenant_id, None, "signing_certificate", environment)
        ):
            warnings.append(
                "This version must be signed, and no signing certificate is stored yet; submission will block."
            )

        existing = s.scalar(
            select(Document).where(
                Document.taxpayer_id == taxpayer.id,
                Document.environment == environment,
                Document.code_number == invoice.code_number,
            )
        )
        if existing is not None and existing.status not in ("draft", "invalid"):
            raise Conflict(
                f"Invoice number {invoice.code_number} is already {existing.status} in MyInvois {environment}. "
                "Use a new number, or a credit or debit note to adjust it."
            )
        doc = existing or Document(
            tenant_id=principal.tenant_id,
            taxpayer_id=taxpayer.id,
            environment=environment,
            code_number=invoice.code_number,
        )
        doc.document_type = invoice.document_type
        doc.version = invoice.version
        doc.status = "draft"
        doc.input = invoice.model_dump(mode="json")
        doc.ubl_json = data.decode("utf-8")
        doc.payload_hash = sha256_hex(data)
        doc.currency = invoice.currency
        doc.payable_amount = totals.payable
        doc.buyer_tin = invoice.buyer.tin
        doc.buyer_name = invoice.buyer.name
        doc.issued_at = issued_at
        doc.errors = []
        doc.submission_uid = doc.uuid = doc.long_id = None
        doc.submitted_at = doc.validated_at = doc.cancelled_at = None
        s.add(doc)
        s.flush()
        self._audit(
            s,
            principal,
            "einvoice.draft",
            "draft",
            doc,
            code_number=doc.code_number,
            document_type=doc.document_type,
            payable=str(totals.payable),
            currency=doc.currency,
            buyer_tin=doc.buyer_tin,
            payload_hash=doc.payload_hash,
        )
        preview = {
            **self._view(doc),
            "issuer": {"tin": taxpayer.tin, "name": taxpayer.name},
            "line_count": len(invoice.lines),
            "totals": {
                "line_extension": str(totals.line_extension),
                "tax": str(totals.tax),
                "payable": str(totals.payable),
            },
            "signed": version["signed"],
            "payload_hash": doc.payload_hash,
            "warnings": warnings,
        }
        return envelope(
            "success",
            data=preview,
            next_action=f"Show the preview to the user, then einvoice_submit(document_id='{doc.id}').",
            resource_id=doc.id,
        )

    def draft_consolidated(
        self,
        principal: Principal,
        *,
        taxpayer_tin: str,
        environment: str,
        month: str,
        supplier: Party,
        receipts: list[Receipt],
        code_number: str,
        version: str = "1.0",
    ) -> dict[str, Any]:
        def go(s: Session) -> dict[str, Any]:
            try:
                result = plan_consolidation(
                    month=month, receipts=receipts, supplier=supplier, code_number=code_number, version=version
                )
            except ValueError as exc:
                raise InvalidInput(str(exc)) from exc
            extra = {
                "period": {"start": result.period_start.isoformat(), "end": result.period_end.isoformat()},
                "submit_by": result.submit_by.isoformat(),
                "receipts_consolidated": len(receipts) - len(result.individual_required),
                "individual_einvoice_required": [
                    {"reference": r.reference, "issued_on": r.issued_on.isoformat(), "gross": str(r.gross)}
                    for r in result.individual_required
                ],
            }
            if result.invoice is None:
                return envelope(
                    "success",
                    data=extra,
                    next_action="Every receipt is above RM10,000; draft an individual e-invoice for each.",
                )
            drafted = self._draft(s, principal, taxpayer_tin, environment, result.invoice)
            drafted["data"].update(extra)
            if result.individual_required:
                drafted["next_action"] = (
                    f"{drafted['next_action']} Then draft individual e-invoices for the "
                    f"{len(result.individual_required)} receipts above RM10,000."
                )
            return drafted

        return self._run(principal, "einvoice.draft_consolidated", go)

    # -- consequential actions ------------------------------------------------------------------

    def submit(self, principal: Principal, *, document_id: str, idempotency_key: str | None = None) -> dict[str, Any]:
        def go(s: Session) -> dict[str, Any]:
            return idempotency.run_once(
                s,
                tenant_id=principal.tenant_id,
                scope="einvoice.submit",
                key=idempotency_key,
                payload={"document_id": document_id},
                fn=lambda: self._submit(s, principal, document_id),
                replay_if=lambda r: r["status"] in ("success", "awaiting_external_event", "invalid"),
            )

        return self._run(principal, "einvoice.submit", go)

    def _submit(self, s: Session, principal: Principal, document_id: str) -> dict[str, Any]:
        now = self.rt.clock()
        doc = self._document(s, principal, document_id)
        taxpayer = s.get(Taxpayer, doc.taxpayer_id)
        assert taxpayer is not None
        _, appointment = self._mandate(s, principal, taxpayer.tin, "submit_documents", now)
        if doc.status in ("submitted", "valid", "cancelled"):
            return envelope(
                "success",
                data=self._view(doc),
                next_action=f"Already {doc.status}. Use einvoice_refresh_status(document_id='{doc.id}').",
                resource_id=doc.id,
            )
        if doc.status != "draft":
            raise Conflict(f"Document is {doc.status}; fix it with einvoice_draft before submitting again.")
        age = now - as_utc(doc.issued_at)
        if age > timedelta(hours=codes.ISSUE_WINDOW_HOURS) or age < -timedelta(minutes=5):
            return envelope(
                "blocked",
                data=self._view(doc),
                blocking_reason="MyInvois only accepts documents issued within the last 72 hours.",
                next_action="Draft it again with a current issue time (for past periods, use an SVDP version).",
                resource_id=doc.id,
            )

        approval, stop = self._gate(
            s,
            principal,
            action="einvoice.submit",
            environment=doc.environment,
            resource_id=doc.id,
            payload_hash=doc.payload_hash,
            summary={
                "title": (
                    f"Submit {codes.DOCUMENT_TYPES[doc.document_type]} {doc.code_number} "
                    f"to MyInvois ({doc.environment})"
                ),
                "issuer": f"{taxpayer.name} ({taxpayer.tin})",
                "buyer": f"{doc.buyer_name} ({doc.buyer_tin})",
                "amount": f"{doc.currency} {doc.payable_amount}",
            },
            amount=doc.payable_amount,
            now=now,
        )
        if stop is not None:
            self._audit(s, principal, "einvoice.submit", stop["status"], doc)
            return stop

        creds, on_behalf_of = self._client_credentials(s, taxpayer, appointment, doc.environment)
        document_bytes = doc.ubl_json.encode("utf-8")
        if codes.VERSIONS[doc.version]["signed"]:
            signed = sign_document(json.loads(document_bytes), self._signing_key(s, taxpayer, doc.environment), now)
            if not verify_document(signed):
                raise UpstreamError("Signature self-check failed; the document was not submitted.")
            document_bytes = serialize(signed)
            if len(document_bytes) > codes.MAX_DOCUMENT_BYTES:
                raise InvalidInput("The signed document is over MyInvois's 300 KB limit.")

        result = self.rt.myinvois(doc.environment).submit(
            creds, on_behalf_of, [submission_entry(document_bytes, doc.code_number)]
        )
        if approval is not None:
            self.approvals.consume(s, approval, now=now)
        doc.submission_uid = result.get("submissionUid")
        doc.submitted_at = now
        accepted = {d.get("invoiceCodeNumber"): d for d in result.get("acceptedDocuments") or []}
        rejected = {d.get("invoiceCodeNumber"): d for d in result.get("rejectedDocuments") or []}
        if doc.code_number in accepted:
            doc.uuid = accepted[doc.code_number].get("uuid")
            doc.status = "submitted"
            self._audit(
                s, principal, "einvoice.submit", "submitted", doc, uuid=doc.uuid, submission_uid=doc.submission_uid
            )
            return envelope(
                "awaiting_external_event",
                data=self._view(doc),
                next_action=(
                    f"MyInvois is validating. Call einvoice_refresh_status(document_id='{doc.id}') in a few seconds."
                ),
                resource_id=doc.id,
                source_system="myinvois",
            )
        doc.status = "invalid"
        doc.errors = _flatten_errors(rejected.get(doc.code_number, {}).get("error") or result) or [
            "Rejected without details."
        ]
        self._audit(s, principal, "einvoice.submit", "rejected", doc, errors=doc.errors)
        return envelope(
            "invalid",
            data=self._view(doc),
            blocking_reason="MyInvois rejected the submission.",
            next_action="Fix the fields in data.errors and call einvoice_draft again with the same code_number.",
            resource_id=doc.id,
            source_system="myinvois",
        )

    def refresh_status(self, principal: Principal, *, document_id: str) -> dict[str, Any]:
        return self._run(principal, "einvoice.refresh_status", lambda s: self._refresh(s, principal, document_id))

    def _refresh(self, s: Session, principal: Principal, document_id: str) -> dict[str, Any]:
        now = self.rt.clock()
        doc = self._document(s, principal, document_id)
        taxpayer = s.get(Taxpayer, doc.taxpayer_id)
        assert taxpayer is not None
        _, appointment = self._mandate(s, principal, taxpayer.tin, "view_documents", now)
        if doc.status == "draft":
            return envelope(
                "success",
                data=self._view(doc),
                next_action=f"einvoice_submit(document_id='{doc.id}')",
                resource_id=doc.id,
            )
        if doc.status not in ("submitted", "valid") or not doc.submission_uid:
            return envelope("success", data=self._view(doc), resource_id=doc.id)

        creds, on_behalf_of = self._client_credentials(s, taxpayer, appointment, doc.environment)
        client = self.rt.myinvois(doc.environment)
        submission = client.get_submission(creds, on_behalf_of, doc.submission_uid)
        entry = next(
            (
                d
                for d in submission.get("documentSummary") or []
                if (doc.uuid and d.get("uuid") == doc.uuid) or d.get("internalId") == doc.code_number
            ),
            None,
        )
        remote = str((entry or {}).get("status") or "").lower()
        previous = doc.status
        if remote == "valid":
            doc.status = "valid"
            doc.uuid = entry.get("uuid") or doc.uuid
            doc.long_id = entry.get("longId") or doc.long_id
            doc.validated_at = doc.validated_at or _parse_time(entry.get("dateTimeValidated")) or now
        elif remote == "invalid":
            details = client.document_details(creds, on_behalf_of, doc.uuid) if doc.uuid else {}
            doc.status = "invalid"
            doc.errors = _flatten_errors(details.get("validationResults") or details) or ["Invalid without details."]
        elif remote == "cancelled":
            doc.status = "cancelled"
            doc.cancelled_at = doc.cancelled_at or _parse_time(entry.get("dateTimeCancelled")) or now
        if doc.status != previous:
            self._audit(s, principal, "einvoice.status", doc.status, doc, uuid=doc.uuid)

        if doc.status == "submitted":
            return envelope(
                "awaiting_external_event",
                data=self._view(doc),
                next_action="Still validating. Check again in a few seconds.",
                resource_id=doc.id,
                source_system="myinvois",
            )
        if doc.status == "invalid":
            return envelope(
                "invalid",
                data=self._view(doc),
                blocking_reason="MyInvois found the document invalid.",
                next_action="Fix the fields in data.errors and call einvoice_draft again with the same code_number.",
                resource_id=doc.id,
                source_system="myinvois",
            )
        return envelope("success", data=self._view(doc), resource_id=doc.id, source_system="myinvois")

    def cancel(
        self, principal: Principal, *, document_id: str, reason: str, idempotency_key: str | None = None
    ) -> dict[str, Any]:
        def go(s: Session) -> dict[str, Any]:
            return idempotency.run_once(
                s,
                tenant_id=principal.tenant_id,
                scope="einvoice.cancel",
                key=idempotency_key,
                payload={"document_id": document_id, "reason": reason},
                fn=lambda: self._cancel(s, principal, document_id, reason),
                replay_if=lambda r: r["status"] == "success",
            )

        return self._run(principal, "einvoice.cancel", go)

    def _cancel(self, s: Session, principal: Principal, document_id: str, reason: str) -> dict[str, Any]:
        now = self.rt.clock()
        reason = (reason or "").strip()
        if not reason or len(reason) > 300:
            raise InvalidInput("A cancellation reason of 1-300 characters is required.")
        doc = self._document(s, principal, document_id)
        taxpayer = s.get(Taxpayer, doc.taxpayer_id)
        assert taxpayer is not None
        _, appointment = self._mandate(s, principal, taxpayer.tin, "cancel_documents", now)
        if doc.status == "cancelled":
            return envelope("success", data=self._view(doc), resource_id=doc.id)
        if doc.status != "valid" or not doc.uuid:
            raise Conflict(f"Only validated documents can be cancelled; this one is {doc.status}.")
        if now - as_utc(doc.validated_at) > timedelta(hours=codes.CANCEL_WINDOW_HOURS):
            return envelope(
                "blocked",
                data=self._view(doc),
                blocking_reason="The 72-hour cancellation window has passed.",
                next_action=f"Draft a credit note (document_type '02') with original_document code_number "
                f"'{doc.code_number}' and uuid '{doc.uuid}'.",
                resource_id=doc.id,
            )
        payload_hash = hashlib.sha256(json.dumps({"uuid": doc.uuid, "reason": reason}).encode()).hexdigest()
        approval, stop = self._gate(
            s,
            principal,
            action="einvoice.cancel",
            environment=doc.environment,
            resource_id=doc.id,
            payload_hash=payload_hash,
            summary={
                "title": (
                    f"Cancel {codes.DOCUMENT_TYPES[doc.document_type]} {doc.code_number} "
                    f"in MyInvois ({doc.environment})"
                ),
                "buyer": f"{doc.buyer_name} ({doc.buyer_tin})",
                "amount": f"{doc.currency} {doc.payable_amount}",
                "reason": reason,
            },
            amount=None,
            now=now,
        )
        if stop is not None:
            self._audit(s, principal, "einvoice.cancel", stop["status"], doc)
            return stop
        creds, on_behalf_of = self._client_credentials(s, taxpayer, appointment, doc.environment)
        self.rt.myinvois(doc.environment).cancel(creds, on_behalf_of, doc.uuid, reason)
        if approval is not None:
            self.approvals.consume(s, approval, now=now)
        doc.status = "cancelled"
        doc.cancelled_at = now
        self._audit(s, principal, "einvoice.cancel", "cancelled", doc, reason=reason)
        return envelope("success", data=self._view(doc), resource_id=doc.id, source_system="myinvois")

    def reject_received(
        self,
        principal: Principal,
        *,
        taxpayer_tin: str,
        environment: str,
        document_uuid: str,
        reason: str,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        def go(s: Session) -> dict[str, Any]:
            return idempotency.run_once(
                s,
                tenant_id=principal.tenant_id,
                scope="einvoice.reject",
                key=idempotency_key,
                payload={"uuid": document_uuid, "reason": reason, "tin": taxpayer_tin, "env": environment},
                fn=lambda: self._reject(s, principal, taxpayer_tin, environment, document_uuid, reason),
                replay_if=lambda r: r["status"] == "success",
            )

        return self._run(principal, "einvoice.reject", go)

    def _reject(
        self, s: Session, principal: Principal, taxpayer_tin: str, environment: str, document_uuid: str, reason: str
    ) -> dict[str, Any]:
        self._check_env(environment)
        now = self.rt.clock()
        reason = (reason or "").strip()
        if not reason or len(reason) > 300:
            raise InvalidInput("A rejection reason of 1-300 characters is required.")
        taxpayer, appointment = self._mandate(s, principal, taxpayer_tin, "reject_documents", now)
        creds, on_behalf_of = self._client_credentials(s, taxpayer, appointment, environment)
        client = self.rt.myinvois(environment)
        details = client.document_details(creds, on_behalf_of, document_uuid)
        receiver = details.get("receiverId") or details.get("receiverTin") or details.get("buyerTin")
        if receiver and normalise_tin(str(receiver)) != taxpayer.tin:
            raise Forbidden("Only the buyer can reject a document, and this one was issued to someone else.")
        validated = _parse_time(details.get("dateTimeValidated"))
        if validated and now - validated > timedelta(hours=codes.CANCEL_WINDOW_HOURS):
            return envelope(
                "blocked",
                blocking_reason="The 72-hour rejection window has passed.",
                next_action="Ask the supplier to issue a credit note instead.",
            )
        payload_hash = hashlib.sha256(json.dumps({"uuid": document_uuid, "reason": reason}).encode()).hexdigest()
        approval, stop = self._gate(
            s,
            principal,
            action="einvoice.reject",
            environment=environment,
            resource_id=document_uuid,
            payload_hash=payload_hash,
            summary={
                "title": f"Reject received e-invoice {details.get('internalId', document_uuid)} ({environment})",
                "supplier": f"{details.get('supplierName') or details.get('issuerName') or ''} "
                f"({details.get('supplierTin') or details.get('issuerTin') or 'unknown'})",
                "amount": str(details.get("totalPayableAmount") or details.get("total") or "unknown"),
                "reason": reason,
            },
            amount=None,
            now=now,
        )
        if stop is not None:
            self._audit(s, principal, "einvoice.reject", stop["status"], uuid=document_uuid)
            return stop
        client.reject(creds, on_behalf_of, document_uuid, reason)
        if approval is not None:
            self.approvals.consume(s, approval, now=now)
        self._audit(s, principal, "einvoice.reject", "rejection_requested", uuid=document_uuid, reason=reason)
        return envelope(
            "success",
            data={"uuid": document_uuid, "status": "rejection_requested"},
            next_action="The supplier must now cancel it or issue a credit note.",
            source_system="myinvois",
        )
