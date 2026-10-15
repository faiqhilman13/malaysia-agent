from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Callable
from urllib.parse import quote

from .config import Settings
from .db import Repository
from .fixtures import (
    HALAL_FNB_PILOT_DATASET,
    HALAL_FRAMEWORK_RULES,
    HALAL_REQUIRED_SUPPORTING_DOCUMENTS,
    HALAL_WORKFLOW_STAGES,
    TRADE_DOC_RULES,
)
from .providers import CIDBClient, MyInvoisClient, RemoteApiError


class InputError(ValueError):
    pass


class NotFoundError(LookupError):
    pass


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def as_money(value: Any) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class OperationsService:
    ACTIONS = {
        "workflows.run": "workflows_run",
        "workflows.status": "workflows_status",
        "approvals.list": "approvals_list",
        "approvals.approve": "approvals_approve",
        "approvals.reject": "approvals_reject",
        "entities.resolve": "resolve_entity",
        "entities.verify_taxpayer": "verify_taxpayer",
        "entities.verify_business_registry": "verify_business_registry",
        "invoices.validate": "validate_invoice",
        "invoices.submit": "submit_invoice",
        "invoices.status": "invoice_status",
        "invoices.cancel": "cancel_invoice",
        "payments.create_request": "create_payment_request",
        "payments.ingest_event": "ingest_payment_event",
        "payments.reconcile": "reconcile_payment",
        "exceptions.list": "list_exceptions",
        "exceptions.resolve": "resolve_exception",
        "trade.doc_pack.validate": "trade_doc_pack_validate",
        "trade.submission.status": "trade_submission_status",
        "halal.status.lookup": "halal_status_lookup",
        "halal.evidence_pack.generate": "halal_evidence_pack_generate",
        "halal.suppliers.upsert": "halal_suppliers_upsert",
        "halal.suppliers.list": "halal_suppliers_list",
        "halal.bom.graph.generate": "halal_bom_graph_generate",
        "halal.renewals.list": "halal_renewals_list",
        "halal.workflows.create": "halal_workflows_create",
        "halal.workflows.status": "halal_workflows_status",
        "halal.checklists.evaluate": "halal_checklists_evaluate",
        "halal.audits.create_query": "halal_audits_create_query",
        "halal.audits.respond_query": "halal_audits_respond_query",
        "halal.documents.share": "halal_documents_share",
        "halal.export_dossier.generate": "halal_export_dossier_generate",
        "halal.dashboard.snapshot": "halal_dashboard_snapshot",
        "halal.pilot.seed_fnb": "halal_pilot_seed_fnb",
        "providers.myinvois.login": "provider_myinvois_login",
        "providers.myinvois.document_types": "provider_myinvois_document_types",
        "providers.myinvois.validate_tin": "provider_myinvois_validate_tin",
        "providers.myinvois.search_tin": "provider_myinvois_search_tin",
        "providers.myinvois.submit_documents": "provider_myinvois_submit_documents",
        "providers.myinvois.get_submission": "provider_myinvois_get_submission",
        "providers.myinvois.cancel_document": "provider_myinvois_cancel_document",
        "providers.cidb.states": "provider_cidb_states",
        "providers.cidb.labour_wage_rate": "provider_cidb_labour_wage_rate",
        "providers.cidb.building_material_price": "provider_cidb_building_material_price",
        "providers.cidb.machinery_rates": "provider_cidb_machinery_rates",
    }

    ACTION_ALIASES = {
        "resolve_entity": "entities.resolve",
        "verify_taxpayer": "entities.verify_taxpayer",
        "verify_business_registry": "entities.verify_business_registry",
    }

    READ_ONLY_ACTIONS = {
        "workflows.status",
        "approvals.list",
        "entities.resolve",
        "entities.verify_taxpayer",
        "entities.verify_business_registry",
        "invoices.validate",
        "invoices.status",
        "exceptions.list",
        "trade.submission.status",
        "providers.myinvois.document_types",
        "providers.myinvois.validate_tin",
        "providers.myinvois.search_tin",
        "providers.myinvois.get_submission",
        "providers.cidb.states",
        "providers.cidb.labour_wage_rate",
        "providers.cidb.building_material_price",
        "providers.cidb.machinery_rates",
        "halal.status.lookup",
        "halal.suppliers.list",
        "halal.renewals.list",
        "halal.workflows.status",
        "halal.dashboard.snapshot",
    }

    EXTERNAL_WAIT_REASONS = {
        "awaiting_remote_processing",
        "awaiting_payment_event",
        "awaiting_final_payment_status",
    }

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.repo = Repository(settings.db_path)

    def invoke(self, action: str, payload: dict[str, Any] | None) -> dict[str, Any]:
        canonical_action = self._canonical_action_name(action)
        payload = payload or {}
        method_name = self.ACTIONS.get(canonical_action)
        if not method_name:
            raise InputError(f"Unknown action: {action}")
        approval_block = self._maybe_block_for_approval(canonical_action, payload)
        if approval_block:
            return approval_block
        method: Callable[[dict[str, Any]], dict[str, Any]] = getattr(self, method_name)
        return method(payload)

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "source_system": "malaysia_agent_ops",
            "timestamp": now_iso(),
        }

    def _provider_error_envelope(self, *, source_system: str, exc: RemoteApiError, next_action: str | None = None) -> dict[str, Any]:
        return self._envelope(
            status="blocked",
            source_system=source_system,
            next_action=next_action,
            blocking_reason="remote_api_error",
            data={
                "error": str(exc),
                "status_code": exc.status_code,
                "body": exc.body,
            },
        )

    def _envelope(
        self,
        *,
        status: str,
        source_system: str,
        data: dict[str, Any] | None = None,
        next_action: str | None = None,
        blocking_reason: str | None = None,
        resource_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "status": status,
            "next_action": next_action,
            "blocking_reason": blocking_reason,
            "source_system": source_system,
            "resource_id": resource_id,
            "timestamp": now_iso(),
            "data": data or {},
        }

    def _create_exception(
        self,
        *,
        exception_type: str,
        resource_type: str,
        resource_id: str,
        summary: str,
        source_system: str,
        details: dict[str, Any],
        severity: str = "high",
    ) -> str:
        exception_id = str(uuid.uuid4())
        timestamp = now_iso()
        self.repo.create_exception(
            {
                "id": exception_id,
                "exception_type": exception_type,
                "workflow_status": "open",
                "severity": severity,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "summary": summary,
                "source_system": source_system,
                "details_json": details,
                "resolution_note": None,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        )
        return exception_id

    def workflows_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        root_action = self._canonical_action_name(payload.get("action"))
        if root_action not in self.ACTIONS:
            raise InputError("action is required and must be a valid action name.")
        root_payload = payload.get("payload") if "payload" in payload else {
            key: value for key, value in payload.items() if key not in {"action", "max_steps"}
        }
        if not isinstance(root_payload, dict):
            raise InputError("payload must be an object.")
        max_steps = min(
            max(1, int(payload.get("max_steps") or self.settings.workflow_runner_max_steps)),
            50,
        )

        run_id = str(uuid.uuid4())
        timestamp = now_iso()
        self.repo.create_workflow_run(
            {
                "id": run_id,
                "root_action": root_action,
                "current_action": root_action,
                "workflow_status": "running",
                "source_system": "workflow_runner",
                "next_action": root_action,
                "blocking_reason": None,
                "initial_payload_json": root_payload,
                "final_output_json": None,
                "execution_log_json": [],
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        )

        execution_log: list[dict[str, Any]] = []
        current_action = root_action
        current_payload = dict(root_payload)
        root_context = dict(root_payload)
        final_response: dict[str, Any] | None = None
        workflow_status = "failed"
        seen_transitions: set[tuple[str, str | None]] = set()

        for step_number in range(1, max_steps + 1):
            response = self.invoke(current_action, current_payload)
            final_response = response
            execution_log.append(
                {
                    "step": step_number,
                    "action": current_action,
                    "payload": current_payload,
                    "response": response,
                }
            )
            self.repo.update_workflow_run(
                run_id,
                current_action=current_action,
                next_action=response.get("next_action"),
                blocking_reason=response.get("blocking_reason"),
                execution_log_json=execution_log,
                final_output_json=response,
                updated_at=now_iso(),
            )

            next_action = self._canonical_action_name(response.get("next_action"))
            if response["status"] == "blocked":
                if response.get("blocking_reason") in self.EXTERNAL_WAIT_REASONS:
                    workflow_status = "awaiting_external_event"
                elif response.get("data", {}).get("approval_id"):
                    workflow_status = "awaiting_human_approval"
                else:
                    workflow_status = "blocked"
                break

            if not next_action:
                workflow_status = "completed"
                break

            if next_action not in self.ACTIONS:
                workflow_status = "blocked"
                final_response = self._envelope(
                    status="blocked",
                    source_system="workflow_runner",
                    next_action=response.get("next_action"),
                    blocking_reason="next_action_not_exposed",
                    data={
                        "run_id": run_id,
                        "unsupported_next_action": response.get("next_action"),
                    },
                )
                execution_log.append(
                    {
                        "step": step_number,
                        "action": "workflow_runner.guard",
                        "payload": {},
                        "response": final_response,
                    }
                )
                break

            derived_payload = self._derive_runner_payload(
                root_payload=root_context,
                current_action=current_action,
                current_payload=current_payload,
                response=response,
                next_action=next_action,
            )
            if derived_payload is None:
                workflow_status = "awaiting_external_event"
                final_response = self._envelope(
                    status="blocked",
                    source_system="workflow_runner",
                    next_action=next_action,
                    blocking_reason="missing_external_input_for_next_action",
                    data={"run_id": run_id, "next_action": next_action},
                )
                execution_log.append(
                    {
                        "step": step_number,
                        "action": "workflow_runner.guard",
                        "payload": {},
                        "response": final_response,
                    }
                )
                break

            transition_key = (current_action, next_action)
            if transition_key in seen_transitions and next_action == current_action:
                workflow_status = "blocked"
                final_response = self._envelope(
                    status="blocked",
                    source_system="workflow_runner",
                    next_action=next_action,
                    blocking_reason="runner_loop_detected",
                    data={"run_id": run_id, "transition": transition_key},
                )
                execution_log.append(
                    {
                        "step": step_number,
                        "action": "workflow_runner.guard",
                        "payload": {},
                        "response": final_response,
                    }
                )
                break
            seen_transitions.add(transition_key)
            current_action = next_action
            current_payload = derived_payload
        else:
            workflow_status = "failed"
            final_response = self._envelope(
                status="blocked",
                source_system="workflow_runner",
                blocking_reason="runner_max_steps_exceeded",
                data={"run_id": run_id, "max_steps": max_steps},
            )

        self.repo.update_workflow_run(
            run_id,
            workflow_status=workflow_status,
            current_action=current_action,
            next_action=final_response.get("next_action") if final_response else None,
            blocking_reason=final_response.get("blocking_reason") if final_response else None,
            final_output_json=final_response,
            execution_log_json=execution_log,
            updated_at=now_iso(),
        )
        return self._envelope(
            status="success" if workflow_status == "completed" else "blocked",
            source_system="workflow_runner",
            next_action=final_response.get("next_action") if final_response else None,
            blocking_reason=final_response.get("blocking_reason") if final_response else None,
            data={
                "run_id": run_id,
                "workflow_status": workflow_status,
                "steps_executed": len(execution_log),
                "final_response": final_response,
                "execution_log": execution_log,
            },
            resource_id=run_id,
        )

    def workflows_status(self, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = payload.get("run_id")
        if not run_id:
            raise InputError("run_id is required.")
        run = self.repo.get_workflow_run(str(run_id))
        if not run:
            raise NotFoundError(f"Unknown run_id: {run_id}")
        return self._envelope(
            status="success",
            source_system="workflow_runner",
            next_action=run.get("next_action"),
            blocking_reason=run.get("blocking_reason"),
            data={"run": run},
            resource_id=str(run_id),
        )

    def approvals_list(self, payload: dict[str, Any]) -> dict[str, Any]:
        items = self.repo.list_approvals(
            workflow_status=payload.get("workflow_status"),
            action=payload.get("action"),
            limit=int(payload.get("limit") or 50),
        )
        return self._envelope(
            status="success",
            source_system="approval_store",
            data={"items": items},
        )

    def approvals_approve(self, payload: dict[str, Any]) -> dict[str, Any]:
        approval_id = payload.get("approval_id")
        identity = payload.get("identity") or {}
        if not approval_id:
            raise InputError("approval_id is required.")
        if not isinstance(identity, dict):
            raise InputError("identity must be an object.")
        approval = self.repo.get_approval(str(approval_id))
        if not approval:
            raise NotFoundError(f"Unknown approval_id: {approval_id}")
        if not identity.get("verified"):
            return self._envelope(
                status="blocked",
                source_system="approval_store",
                next_action="approvals.approve",
                blocking_reason="identity_not_verified",
                data={"approval": approval},
                resource_id=str(approval_id),
            )
        self.repo.update_approval(
            str(approval_id),
            workflow_status="approved",
            approval_context_json=identity,
            decision_context_json={
                "decision": "approved",
                "note": payload.get("note"),
                "approved_at": now_iso(),
            },
            updated_at=now_iso(),
        )
        approved = self.repo.get_approval(str(approval_id))
        return self._envelope(
            status="success",
            source_system="approval_store",
            next_action=approved["action"],
            data={"approval": approved},
            resource_id=str(approval_id),
        )

    def approvals_reject(self, payload: dict[str, Any]) -> dict[str, Any]:
        approval_id = payload.get("approval_id")
        identity = payload.get("identity") or {}
        if not approval_id:
            raise InputError("approval_id is required.")
        if not isinstance(identity, dict):
            raise InputError("identity must be an object.")
        approval = self.repo.get_approval(str(approval_id))
        if not approval:
            raise NotFoundError(f"Unknown approval_id: {approval_id}")
        self.repo.update_approval(
            str(approval_id),
            workflow_status="rejected",
            approval_context_json=identity or None,
            decision_context_json={
                "decision": "rejected",
                "note": payload.get("note"),
                "rejected_at": now_iso(),
            },
            updated_at=now_iso(),
        )
        rejected = self.repo.get_approval(str(approval_id))
        return self._envelope(
            status="success",
            source_system="approval_store",
            data={"approval": rejected},
            resource_id=str(approval_id),
        )

    def resolve_entity(self, payload: dict[str, Any]) -> dict[str, Any]:
        query = (
            payload.get("query")
            or payload.get("name")
            or payload.get("tin")
            or payload.get("registration_no")
        )
        if not query:
            raise InputError("Provide query, name, tin, or registration_no.")

        matches = self.repo.search_entities(str(query))
        if not matches:
            return self._envelope(
                status="blocked",
                source_system=self.settings.business_registry_source_system,
                next_action="provide_more_specific_entity_identifier",
                blocking_reason="no_matching_entity_found",
                data={"matches": []},
            )

        primary = matches[0]
        return self._envelope(
            status="success",
            source_system=self.settings.business_registry_source_system,
            next_action="entities.verify_taxpayer",
            data={
                "primary_match": self._entity_public(primary),
                "matches": [self._entity_public(item) for item in matches],
            },
            resource_id=primary["tin"],
        )

    def verify_taxpayer(self, payload: dict[str, Any]) -> dict[str, Any]:
        tin = payload.get("tin")
        if not tin:
            raise InputError("tin is required.")
        entity = self.repo.get_entity_by_tin(str(tin))
        if not entity:
            return self._envelope(
                status="blocked",
                source_system=self.settings.myinvois_source_system,
                next_action="resolve_entity",
                blocking_reason="unknown_tin",
                data={"tin": tin},
            )
        if not entity["tax_active"]:
            return self._envelope(
                status="blocked",
                source_system=self.settings.myinvois_source_system,
                next_action="correct_taxpayer_registration",
                blocking_reason="tin_is_not_active",
                data=self._entity_public(entity),
                resource_id=entity["tin"],
            )
        return self._envelope(
            status="success",
            source_system=self.settings.myinvois_source_system,
            next_action="invoices.submit",
            data={
                "taxpayer": self._entity_public(entity),
                "verified": True,
            },
            resource_id=entity["tin"],
        )

    def verify_business_registry(self, payload: dict[str, Any]) -> dict[str, Any]:
        registration_no = payload.get("registration_no")
        tin = payload.get("tin")
        entity = None
        if registration_no:
            entity = self.repo.get_entity_by_registration_no(str(registration_no))
        elif tin:
            entity = self.repo.get_entity_by_tin(str(tin))
        else:
            raise InputError("registration_no or tin is required.")

        if not entity:
            return self._envelope(
                status="blocked",
                source_system=self.settings.business_registry_source_system,
                next_action="resolve_entity",
                blocking_reason="entity_not_found",
                data={},
            )
        if entity["business_registry_status"] != "active":
            return self._envelope(
                status="blocked",
                source_system=self.settings.business_registry_source_system,
                next_action="refresh_business_registry_data",
                blocking_reason="business_registry_status_not_active",
                data=self._entity_public(entity),
                resource_id=entity["registration_no"],
            )
        return self._envelope(
            status="success",
            source_system=self.settings.business_registry_source_system,
            next_action="entities.verify_taxpayer",
            data={
                "business_registry": {
                    **self._entity_public(entity),
                    "business_registry_status": entity["business_registry_status"],
                }
            },
            resource_id=entity["registration_no"],
        )

    def validate_invoice(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized, errors = self._normalize_invoice(payload)
        if errors:
            return self._envelope(
                status="blocked",
                source_system=self.settings.myinvois_source_system,
                next_action="fix_invoice_payload",
                blocking_reason=errors[0],
                data={"errors": errors},
            )
        return self._envelope(
            status="success",
            source_system=self.settings.myinvois_source_system,
            next_action="invoices.submit",
            data={
                "invoice": normalized,
                "validation_errors": [],
            },
            resource_id=normalized["invoice_number"],
        )

    def submit_invoice(self, payload: dict[str, Any]) -> dict[str, Any]:
        execution_mode = self._invoice_execution_mode(payload)
        if execution_mode == "real":
            return self._submit_invoice_real(payload)

        normalized, errors = self._normalize_invoice(payload)
        invoice_number = str(payload.get("invoice_number") or "unknown")
        if errors:
            exception_id = self._create_exception(
                exception_type="invoice_validation_failure",
                resource_type="invoice",
                resource_id=invoice_number,
                summary="Invoice submission blocked by validation errors.",
                source_system=self.settings.myinvois_source_system,
                details={"errors": errors},
            )
            return self._envelope(
                status="blocked",
                source_system=self.settings.myinvois_source_system,
                next_action="fix_invoice_payload",
                blocking_reason=errors[0],
                data={"errors": errors, "exception_id": exception_id},
                resource_id=invoice_number,
            )

        submission_id = str(uuid.uuid4())
        external_submission_id = f"SUB-{submission_id.split('-')[0].upper()}"
        timestamp = now_iso()
        record = {
            "id": submission_id,
            "invoice_number": normalized["invoice_number"],
            "supplier_tin": normalized["supplier_tin"],
            "buyer_tin": normalized["buyer_tin"],
            "currency": normalized["currency"],
            "total_amount": normalized["total_amount"],
            "workflow_status": "submitted",
            "source_system": self.settings.myinvois_source_system,
            "next_action": "invoices.status",
            "blocking_reason": None,
            "poll_count": 0,
            "external_submission_id": external_submission_id,
            "external_document_id": None,
            "payload_json": normalized,
                "validation_json": {"errors": []},
                "execution_mode": "sandbox",
                "created_at": timestamp,
                "updated_at": timestamp,
                "canceled_at": None,
            }
        self.repo.create_invoice_submission(record)
        return self._envelope(
            status="success",
            source_system=self.settings.myinvois_source_system,
            next_action="invoices.status",
            data={
                "submission_id": submission_id,
                "submission_status": "submitted",
                "external_submission_id": external_submission_id,
                "execution_mode": "sandbox",
                "invoice": normalized,
            },
            resource_id=submission_id,
        )

    def invoice_status(self, payload: dict[str, Any]) -> dict[str, Any]:
        submission_id = payload.get("submission_id")
        if not submission_id:
            raise InputError("submission_id is required.")
        submission = self.repo.get_invoice_submission(str(submission_id))
        if not submission:
            raise NotFoundError(f"Unknown submission_id: {submission_id}")

        if submission["source_system"] == "myinvois_real":
            return self._invoice_status_real(payload, submission)

        workflow_status = submission["workflow_status"]
        if workflow_status == "submitted" and submission["poll_count"] == 0:
            external_document_id = f"DOC-{submission['id'].split('-')[0].upper()}"
            self.repo.update_invoice_submission(
                submission["id"],
                workflow_status="validated",
                next_action="payments.create_request",
                blocking_reason=None,
                poll_count=submission["poll_count"] + 1,
                external_document_id=external_document_id,
                updated_at=now_iso(),
            )
            submission = self.repo.get_invoice_submission(str(submission_id))
        elif workflow_status == "submitted":
            self.repo.update_invoice_submission(
                submission["id"],
                poll_count=submission["poll_count"] + 1,
                updated_at=now_iso(),
            )
            submission = self.repo.get_invoice_submission(str(submission_id))

        return self._envelope(
            status="success",
            source_system=self.settings.myinvois_source_system,
            next_action=submission["next_action"],
            blocking_reason=submission["blocking_reason"],
            data={
                "submission_id": submission["id"],
                "submission_status": submission["workflow_status"],
                "external_submission_id": submission["external_submission_id"],
                "external_document_id": submission["external_document_id"],
                "invoice_number": submission["invoice_number"],
                "poll_count": submission["poll_count"],
            },
            resource_id=submission["id"],
        )

    def cancel_invoice(self, payload: dict[str, Any]) -> dict[str, Any]:
        submission_id = payload.get("submission_id")
        if not submission_id:
            raise InputError("submission_id is required.")
        submission = self.repo.get_invoice_submission(str(submission_id))
        if not submission:
            raise NotFoundError(f"Unknown submission_id: {submission_id}")

        if submission["source_system"] == "myinvois_real":
            return self._cancel_invoice_real(payload, submission)

        linked_payments = self.repo.list_payment_requests_for_submission(submission["id"])
        if any(item["workflow_status"] in {"matched", "pending", "mismatch"} for item in linked_payments):
            return self._envelope(
                status="blocked",
                source_system=self.settings.myinvois_source_system,
                next_action="refund_or_resolve_existing_payment_request",
                blocking_reason="invoice_has_related_payment_request",
                data={"payment_request_ids": [item["id"] for item in linked_payments]},
                resource_id=submission["id"],
            )

        self.repo.update_invoice_submission(
            submission["id"],
            workflow_status="canceled",
            next_action=None,
            blocking_reason=None,
            canceled_at=now_iso(),
            updated_at=now_iso(),
        )
        return self._envelope(
            status="success",
            source_system=self.settings.myinvois_source_system,
            data={
                "submission_id": submission["id"],
                "submission_status": "canceled",
            },
            resource_id=submission["id"],
        )

    def create_payment_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        submission_id = payload.get("submission_id")
        if not submission_id:
            raise InputError("submission_id is required.")
        submission = self.repo.get_invoice_submission(str(submission_id))
        if not submission:
            raise NotFoundError(f"Unknown submission_id: {submission_id}")
        if submission["workflow_status"] != "validated":
            return self._envelope(
                status="blocked",
                source_system=self.settings.paynet_source_system,
                next_action="invoices.status",
                blocking_reason="invoice_not_ready_for_payment_request",
                data={"submission_status": submission["workflow_status"]},
                resource_id=submission["id"],
            )

        request_id = str(uuid.uuid4())
        amount = as_money(payload.get("amount") or submission["total_amount"])
        reference = f"PAY-{request_id.split('-')[0].upper()}"
        qr_payload = self._build_duitnow_request(reference=reference, amount=amount)
        timestamp = now_iso()
        record = {
            "id": request_id,
            "invoice_submission_id": submission["id"],
            "amount": amount,
            "currency": submission["currency"],
            "reference": reference,
            "workflow_status": "pending",
            "qr_payload": qr_payload,
            "received_amount": None,
            "source_system": self.settings.paynet_source_system,
            "metadata_json": {
                "merchant_name": self.settings.merchant_name,
                "merchant_city": self.settings.merchant_city,
                "payment_url": f"duitnow://sandbox/request/{request_id}?amount={amount:.2f}",
            },
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        self.repo.create_payment_request(record)
        self.repo.update_invoice_submission(
            submission["id"],
            workflow_status="payment_requested",
            next_action="payments.ingest_event",
            updated_at=now_iso(),
        )
        suggested_event_payload = {
            "request_id": request_id,
            "reference": reference,
            "event_type": "payment_received",
            "payment_status": "succeeded",
            "amount": amount,
            "currency": submission["currency"],
        }
        return self._envelope(
            status="success",
            source_system=self.settings.paynet_source_system,
            next_action="payments.ingest_event",
            data={
                "request_id": request_id,
                "reference": reference,
                "amount": amount,
                "currency": submission["currency"],
                "qr_payload": qr_payload,
                "payment_url": record["metadata_json"]["payment_url"],
                "event_ingest_endpoint": "/v1/payments/events/ingest",
                "suggested_event_payload": suggested_event_payload,
            },
            resource_id=request_id,
        )

    def ingest_payment_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        request_id = payload.get("request_id")
        reference = payload.get("reference")
        if not request_id and not reference:
            raise InputError("request_id or reference is required.")
        payment_request = (
            self.repo.get_payment_request(str(request_id))
            if request_id
            else self.repo.get_payment_request_by_reference(str(reference))
        )
        if not payment_request:
            identifier = request_id or reference
            raise NotFoundError(f"Unknown payment request: {identifier}")

        payment_status = str(
            payload.get("payment_status")
            or payload.get("status")
            or payload.get("event_type")
            or "payment_received"
        ).strip().lower()
        event_amount = payload.get("amount")
        if event_amount is None and payload.get("received_amount") is not None:
            event_amount = payload.get("received_amount")
        external_reference = payload.get("external_reference")
        updated_at = now_iso()
        event_id = str(uuid.uuid4())
        normalized_amount = as_money(event_amount) if event_amount is not None else None
        self.repo.create_payment_event(
            {
                "id": event_id,
                "request_id": payment_request["id"],
                "reference": payment_request["reference"],
                "provider": payload.get("provider") or self.settings.paynet_source_system,
                "event_type": str(payload.get("event_type") or "payment_event"),
                "workflow_status": payment_status,
                "amount": normalized_amount,
                "currency": payload.get("currency") or payment_request["currency"],
                "external_reference": external_reference,
                "payload_json": payload,
                "created_at": updated_at,
                "updated_at": updated_at,
            }
        )

        if payment_status in {"pending", "processing", "awaiting_settlement"}:
            self.repo.update_payment_request(
                payment_request["id"],
                workflow_status="pending",
                updated_at=updated_at,
            )
            return self._envelope(
                status="blocked",
                source_system=self.settings.paynet_source_system,
                next_action="payments.ingest_event",
                blocking_reason="awaiting_final_payment_status",
                data={
                    "event_id": event_id,
                    "request_id": payment_request["id"],
                    "reference": payment_request["reference"],
                },
                resource_id=payment_request["id"],
            )

        if payment_status in {"failed", "cancelled", "canceled", "rejected"}:
            self.repo.update_payment_request(
                payment_request["id"],
                workflow_status="failed",
                updated_at=updated_at,
            )
            self.repo.update_invoice_submission(
                payment_request["invoice_submission_id"],
                workflow_status="payment_requested",
                next_action="payments.create_request",
                blocking_reason="payment_event_failed",
                updated_at=updated_at,
            )
            return self._envelope(
                status="blocked",
                source_system=self.settings.paynet_source_system,
                next_action="payments.create_request",
                blocking_reason="payment_event_failed",
                data={
                    "event_id": event_id,
                    "request_id": payment_request["id"],
                    "payment_status": payment_status,
                },
                resource_id=payment_request["id"],
            )

        amount = as_money(payment_request["amount"])
        received = as_money(normalized_amount if normalized_amount is not None else amount)
        if received != amount:
            self.repo.update_payment_request(
                payment_request["id"],
                workflow_status="mismatch",
                received_amount=received,
                updated_at=updated_at,
            )
            exception_id = self._create_exception(
                exception_type="payment_mismatch",
                resource_type="payment_request",
                resource_id=payment_request["id"],
                summary="Received amount does not match requested amount.",
                source_system=self.settings.paynet_source_system,
                details={
                    "expected_amount": amount,
                    "received_amount": received,
                    "external_reference": external_reference,
                    "event_id": event_id,
                },
            )
            return self._envelope(
                status="blocked",
                source_system=self.settings.paynet_source_system,
                next_action="exceptions.resolve",
                blocking_reason="received_amount_does_not_match_invoice_total",
                data={
                    "event_id": event_id,
                    "request_id": payment_request["id"],
                    "expected_amount": amount,
                    "received_amount": received,
                    "exception_id": exception_id,
                },
                resource_id=payment_request["id"],
            )

        self.repo.update_payment_request(
            payment_request["id"],
            workflow_status="matched",
            received_amount=received,
            updated_at=updated_at,
        )
        self.repo.update_invoice_submission(
            payment_request["invoice_submission_id"],
            workflow_status="paid",
            next_action=None,
            blocking_reason=None,
            updated_at=updated_at,
        )
        return self._envelope(
            status="success",
            source_system=self.settings.paynet_source_system,
            data={
                "event_id": event_id,
                "request_id": payment_request["id"],
                "workflow_status": "matched",
                "received_amount": received,
                "external_reference": external_reference,
            },
            resource_id=payment_request["id"],
        )

    def reconcile_payment(self, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("received_amount") is None:
            raise InputError("received_amount is required.")
        event_payload = {
            "request_id": payload.get("request_id"),
            "reference": payload.get("reference"),
            "event_type": "manual_reconcile",
            "payment_status": "succeeded",
            "amount": payload.get("received_amount"),
            "currency": payload.get("currency"),
            "external_reference": payload.get("external_reference"),
            "provider": "manual_operator",
        }
        return self.ingest_payment_event(event_payload)

    def list_exceptions(self, payload: dict[str, Any]) -> dict[str, Any]:
        items = self.repo.list_exceptions(
            workflow_status=payload.get("workflow_status"),
            resource_id=payload.get("resource_id"),
        )
        return self._envelope(
            status="success",
            source_system="exception_store",
            data={"items": items},
        )

    def resolve_exception(self, payload: dict[str, Any]) -> dict[str, Any]:
        exception_id = payload.get("exception_id")
        resolution_note = payload.get("resolution_note")
        if not exception_id or not resolution_note:
            raise InputError("exception_id and resolution_note are required.")
        existing = self.repo.get_exception(str(exception_id))
        if not existing:
            raise NotFoundError(f"Unknown exception_id: {exception_id}")
        self.repo.resolve_exception(str(exception_id), str(resolution_note), now_iso())
        resolved = self.repo.get_exception(str(exception_id))
        return self._envelope(
            status="success",
            source_system="exception_store",
            data={"exception": resolved},
            resource_id=str(exception_id),
        )

    def trade_doc_pack_validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        doc_type = payload.get("doc_type")
        documents = payload.get("documents") or {}
        if not doc_type:
            raise InputError("doc_type is required.")
        if not isinstance(documents, dict):
            raise InputError("documents must be an object.")
        required = TRADE_DOC_RULES.get(str(doc_type))
        if not required:
            raise InputError(f"Unsupported doc_type: {doc_type}")

        missing = [name for name in required if not documents.get(name)]
        submission_id = str(uuid.uuid4())
        validation = {
            "required_documents": required,
            "missing_documents": missing,
            "provided_documents": sorted(documents.keys()),
        }
        workflow_status = "ready_for_submission" if not missing else "blocked_missing_documents"
        timestamp = now_iso()
        self.repo.create_trade_submission(
            {
                "id": submission_id,
                "doc_type": doc_type,
                "workflow_status": workflow_status,
                "source_system": self.settings.trade_source_system,
                "validation_json": validation,
                "payload_json": payload,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        )
        return self._envelope(
            status="success" if not missing else "blocked",
            source_system=self.settings.trade_source_system,
            next_action="trade.submission.status" if not missing else "upload_missing_trade_documents",
            blocking_reason="missing_trade_documents" if missing else None,
            data={
                "submission_id": submission_id,
                "doc_type": doc_type,
                "workflow_status": workflow_status,
                "validation": validation,
            },
            resource_id=submission_id,
        )

    def trade_submission_status(self, payload: dict[str, Any]) -> dict[str, Any]:
        submission_id = payload.get("submission_id")
        if not submission_id:
            raise InputError("submission_id is required.")
        submission = self.repo.get_trade_submission(str(submission_id))
        if not submission:
            raise NotFoundError(f"Unknown submission_id: {submission_id}")
        validation = submission["validation_json"]
        return self._envelope(
            status="success",
            source_system=self.settings.trade_source_system,
            next_action=None if submission["workflow_status"] == "ready_for_submission" else "upload_missing_trade_documents",
            blocking_reason="missing_trade_documents" if validation["missing_documents"] else None,
            data={
                "submission_id": submission["id"],
                "doc_type": submission["doc_type"],
                "workflow_status": submission["workflow_status"],
                "validation": validation,
            },
            resource_id=submission["id"],
        )

    def halal_status_lookup(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = self.repo.get_halal_status(
            certificate_ref=payload.get("certificate_ref"),
            company_name=payload.get("company_name"),
            company_tin=payload.get("company_tin"),
        )
        if not record:
            return self._envelope(
                status="blocked",
                source_system=self.settings.halal_source_system,
                next_action="provide_valid_certificate_or_company_identifier",
                blocking_reason="halal_record_not_found",
                data={},
            )
        if record["status"] != "active":
            return self._envelope(
                status="blocked",
                source_system=self.settings.halal_source_system,
                next_action="replace_or_renew_supplier_certificate",
                blocking_reason="halal_certificate_not_active",
                data={"halal_record": record},
                resource_id=record["certificate_ref"],
            )
        return self._envelope(
            status="success",
            source_system=self.settings.halal_source_system,
            next_action="halal.evidence_pack.generate",
            data={"halal_record": record},
            resource_id=record["certificate_ref"],
        )

    def halal_evidence_pack_generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        applicant_name = payload.get("applicant_name")
        product_name = payload.get("product_name")
        bom = payload.get("bom") or []
        supporting_documents = payload.get("supporting_documents") or []
        if not applicant_name or not product_name:
            raise InputError("applicant_name and product_name are required.")
        if not isinstance(bom, list):
            raise InputError("bom must be an array.")
        if not isinstance(supporting_documents, list):
            raise InputError("supporting_documents must be an array.")

        missing_documents = [
            document
            for document in HALAL_REQUIRED_SUPPORTING_DOCUMENTS
            if document not in supporting_documents
        ]
        supplier_checks = []
        supplier_gaps = []
        ingredient_records = []
        renewal_watchlist = []
        for item in bom:
            supplier_resolution = self._resolve_halal_supplier(
                supplier_tin=item.get("supplier_tin"),
                supplier_name=item.get("supplier_name"),
                certificate_ref=item.get("certificate_ref"),
            )
            supplier_record = supplier_resolution["official_record"]
            supplier_profile = supplier_resolution["supplier_profile"]
            supplier_active = supplier_profile.get("certificate_status") == "active"
            days_to_expiry = supplier_profile.get("days_to_expiry")
            supplier_checks.append(
                {
                    "ingredient": item.get("ingredient"),
                    "supplier_tin": supplier_profile.get("supplier_tin"),
                    "supplier_name": supplier_profile.get("supplier_name"),
                    "supplier_halal_status": supplier_profile.get("certificate_status"),
                    "certificate_ref": supplier_profile.get("certificate_ref"),
                    "expiry_date": supplier_profile.get("expiry_date"),
                    "days_to_expiry": days_to_expiry,
                    "risk_level": supplier_profile.get("risk_level"),
                }
            )
            ingredient_records.append(
                {
                    "ingredient": item.get("ingredient"),
                    "ingredient_code": item.get("ingredient_code") or self._slug(item.get("ingredient") or "ingredient"),
                    "supplier_tin": supplier_profile.get("supplier_tin"),
                    "supplier_name": supplier_profile.get("supplier_name"),
                    "certificate_ref": supplier_profile.get("certificate_ref"),
                    "certificate_status": supplier_profile.get("certificate_status"),
                    "requires_manual_review": not supplier_active,
                }
            )
            if not supplier_active:
                supplier_gaps.append(item.get("ingredient") or supplier_profile.get("supplier_name") or "unknown_supplier")
            elif days_to_expiry is not None and days_to_expiry <= 120:
                renewal_watchlist.append(
                    {
                        "ingredient": item.get("ingredient"),
                        "supplier_tin": supplier_profile.get("supplier_tin"),
                        "certificate_ref": supplier_profile.get("certificate_ref"),
                        "days_to_expiry": days_to_expiry,
                    }
                )

        pack_id = str(uuid.uuid4())
        payload_json = {
            "applicant_name": applicant_name,
            "product_name": product_name,
            "bom": bom,
            "supporting_documents": supporting_documents,
            "supplier_checks": supplier_checks,
            "myhalalingredients_records": ingredient_records,
            "missing_documents": missing_documents,
            "supplier_gaps": supplier_gaps,
            "renewal_watchlist": renewal_watchlist,
            "evidence_sections": [
                "company_profile",
                "product_scope",
                "ingredient_matrix",
                "supplier_certificates",
                "supporting_documents",
            ],
        }
        workflow_status = "ready" if not missing_documents and not supplier_gaps else "blocked_missing_evidence"
        self.repo.create_halal_pack(
            {
                "id": pack_id,
                "applicant_name": applicant_name,
                "workflow_status": workflow_status,
                "source_system": self.settings.halal_source_system,
                "payload_json": payload_json,
                "created_at": now_iso(),
            }
        )
        return self._envelope(
            status="success" if workflow_status == "ready" else "blocked",
            source_system=self.settings.halal_source_system,
            next_action=None if workflow_status == "ready" else "collect_missing_halal_evidence",
            blocking_reason="missing_halal_supporting_evidence" if workflow_status != "ready" else None,
            data={
                "pack_id": pack_id,
                "workflow_status": workflow_status,
                "missing_documents": missing_documents,
                "supplier_gaps": supplier_gaps,
                "supplier_checks": supplier_checks,
                "myhalalingredients_records": ingredient_records,
                "renewal_watchlist": renewal_watchlist,
            },
            resource_id=pack_id,
        )

    def halal_suppliers_upsert(self, payload: dict[str, Any]) -> dict[str, Any]:
        supplier_name = payload.get("supplier_name")
        supplier_tin = payload.get("supplier_tin")
        certificate_ref = payload.get("certificate_ref")
        if not supplier_name and not supplier_tin and not certificate_ref:
            raise InputError("supplier_name, supplier_tin, or certificate_ref is required.")

        resolution = self._resolve_halal_supplier(
            supplier_tin=supplier_tin,
            supplier_name=supplier_name,
            certificate_ref=certificate_ref,
        )
        supplier_profile = resolution["supplier_profile"]
        record_id = (
            payload.get("supplier_id")
            or (f"tin:{supplier_profile['supplier_tin']}" if supplier_profile.get("supplier_tin") else None)
            or (f"cert:{supplier_profile['certificate_ref']}" if supplier_profile.get("certificate_ref") else None)
            or str(uuid.uuid4())
        )
        timestamp = now_iso()
        existing = self.repo.get_halal_supplier(str(record_id))
        record = {
            "id": str(record_id),
            "supplier_tin": payload.get("supplier_tin") or supplier_profile.get("supplier_tin"),
            "supplier_name": payload.get("supplier_name") or supplier_profile.get("supplier_name") or str(supplier_name or "Unknown supplier"),
            "certificate_ref": payload.get("certificate_ref") or supplier_profile.get("certificate_ref"),
            "certificate_status": payload.get("certificate_status") or supplier_profile.get("certificate_status") or "unknown",
            "expiry_date": payload.get("expiry_date") or supplier_profile.get("expiry_date"),
            "risk_level": payload.get("risk_level") or supplier_profile.get("risk_level") or "high",
            "products_json": payload.get("products") or supplier_profile.get("products") or [],
            "metadata_json": {
                "notes": payload.get("notes"),
                "contact_name": payload.get("contact_name"),
                "contact_email": payload.get("contact_email"),
                "official_record_found": bool(resolution["official_record"]),
                "days_to_expiry": self._days_until(payload.get("expiry_date")) if payload.get("expiry_date") else supplier_profile.get("days_to_expiry"),
            },
            "source_system": self.settings.halal_source_system,
            "created_at": existing["created_at"] if existing else timestamp,
            "updated_at": timestamp,
        }
        if not payload.get("risk_level"):
            record["risk_level"] = self._risk_level_for_certificate(
                status=str(record["certificate_status"]),
                expiry_date=record["expiry_date"],
            )
            record["metadata_json"]["days_to_expiry"] = self._days_until(record["expiry_date"]) if record["expiry_date"] else None
        self.repo.upsert_halal_supplier(record)

        blocking_reason = None
        next_action = "halal.bom.graph.generate"
        status = "success"
        if record["certificate_status"] == "unknown":
            status = "blocked"
            next_action = "collect_supplier_certificate"
            blocking_reason = "supplier_certificate_not_found"
        elif record["certificate_status"] != "active":
            status = "blocked"
            next_action = "replace_or_renew_supplier_certificate"
            blocking_reason = "supplier_certificate_not_active"

        return self._envelope(
            status=status,
            source_system=self.settings.halal_source_system,
            next_action=next_action,
            blocking_reason=blocking_reason,
            data={"supplier": record},
            resource_id=record["id"],
        )

    def halal_suppliers_list(self, payload: dict[str, Any]) -> dict[str, Any]:
        expiring_within_days = int(payload.get("expiring_within_days") or 0)
        items = self.repo.list_halal_suppliers(risk_level=payload.get("risk_level"))
        if expiring_within_days > 0:
            filtered = []
            for item in items:
                days_to_expiry = self._days_until(item["expiry_date"]) if item.get("expiry_date") else None
                if days_to_expiry is not None and days_to_expiry <= expiring_within_days:
                    enriched = dict(item)
                    enriched["days_to_expiry"] = days_to_expiry
                    filtered.append(enriched)
            items = filtered
        return self._envelope(
            status="success",
            source_system=self.settings.halal_source_system,
            next_action="halal.bom.graph.generate" if items else "halal.suppliers.upsert",
            data={"items": items},
        )

    def halal_bom_graph_generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        applicant_name = payload.get("applicant_name")
        product_name = payload.get("product_name")
        bom = payload.get("bom") or []
        if not applicant_name or not product_name:
            raise InputError("applicant_name and product_name are required.")
        if not isinstance(bom, list) or not bom:
            raise InputError("bom must be a non-empty array.")

        graph_id = str(uuid.uuid4())
        nodes = [
            {"id": f"applicant:{self._slug(str(applicant_name))}", "label": applicant_name, "type": "applicant"},
            {"id": f"product:{self._slug(str(product_name))}", "label": product_name, "type": "product"},
        ]
        edges = [
            {
                "source": f"applicant:{self._slug(str(applicant_name))}",
                "target": f"product:{self._slug(str(product_name))}",
                "relationship": "owns_product",
            }
        ]
        issues = []
        summary = {"ingredients": 0, "suppliers": 0, "active_certificates": 0, "high_risk_suppliers": 0}
        seen_nodes: set[str] = {node["id"] for node in nodes}

        for index, item in enumerate(bom):
            if not isinstance(item, dict):
                raise InputError(f"bom item at index {index} must be an object.")
            ingredient = item.get("ingredient")
            if not ingredient:
                raise InputError(f"bom item at index {index} is missing ingredient.")

            ingredient_id = f"ingredient:{self._slug(str(ingredient))}:{index}"
            if ingredient_id not in seen_nodes:
                nodes.append({"id": ingredient_id, "label": ingredient, "type": "ingredient"})
                seen_nodes.add(ingredient_id)
            edges.append(
                {
                    "source": f"product:{self._slug(str(product_name))}",
                    "target": ingredient_id,
                    "relationship": "contains",
                }
            )
            summary["ingredients"] += 1

            resolution = self._resolve_halal_supplier(
                supplier_tin=item.get("supplier_tin"),
                supplier_name=item.get("supplier_name"),
                certificate_ref=item.get("certificate_ref"),
            )
            supplier_profile = resolution["supplier_profile"]
            supplier_label = supplier_profile.get("supplier_name") or item.get("supplier_name") or "Unknown supplier"
            supplier_id = (
                f"supplier:{self._slug(str(supplier_profile.get('supplier_tin') or supplier_label))}:{index}"
            )
            if supplier_id not in seen_nodes:
                nodes.append(
                    {
                        "id": supplier_id,
                        "label": supplier_label,
                        "type": "supplier",
                        "risk_level": supplier_profile.get("risk_level"),
                    }
                )
                seen_nodes.add(supplier_id)
                summary["suppliers"] += 1
            edges.append({"source": ingredient_id, "target": supplier_id, "relationship": "supplied_by"})

            certificate_ref_value = supplier_profile.get("certificate_ref")
            if certificate_ref_value:
                certificate_id = f"certificate:{self._slug(str(certificate_ref_value))}:{index}"
                if certificate_id not in seen_nodes:
                    nodes.append(
                        {
                            "id": certificate_id,
                            "label": certificate_ref_value,
                            "type": "certificate",
                            "status": supplier_profile.get("certificate_status"),
                            "expiry_date": supplier_profile.get("expiry_date"),
                        }
                    )
                    seen_nodes.add(certificate_id)
                edges.append({"source": supplier_id, "target": certificate_id, "relationship": "backed_by"})

            if supplier_profile.get("certificate_status") == "active":
                summary["active_certificates"] += 1
            else:
                issues.append(
                    {
                        "ingredient": ingredient,
                        "supplier_name": supplier_label,
                        "issue": "supplier_without_active_certificate",
                    }
                )
            if supplier_profile.get("risk_level") == "high":
                summary["high_risk_suppliers"] += 1

        workflow_status = "ready" if not issues else "blocked_non_compliant_bom"
        payload_json = {
            "applicant_name": applicant_name,
            "product_name": product_name,
            "bom": bom,
            "nodes": nodes,
            "edges": edges,
            "issues": issues,
            "summary": summary,
        }
        timestamp = now_iso()
        self.repo.create_halal_bom_graph(
            {
                "id": graph_id,
                "applicant_name": applicant_name,
                "product_name": product_name,
                "workflow_status": workflow_status,
                "source_system": self.settings.halal_source_system,
                "payload_json": payload_json,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        )
        return self._envelope(
            status="success" if not issues else "blocked",
            source_system=self.settings.halal_source_system,
            next_action="halal.evidence_pack.generate" if not issues else "halal.suppliers.upsert",
            blocking_reason="supplier_without_active_certificate" if issues else None,
            data={
                "graph_id": graph_id,
                "workflow_status": workflow_status,
                "summary": summary,
                "issues": issues,
                "nodes": nodes,
                "edges": edges,
            },
            resource_id=graph_id,
        )

    def halal_renewals_list(self, payload: dict[str, Any]) -> dict[str, Any]:
        within_days = int(payload.get("within_days") or 120)
        items = []
        seen_keys = set()

        for registry_item in self.repo.list_halal_suppliers():
            key = registry_item.get("certificate_ref") or registry_item.get("supplier_tin") or registry_item["id"]
            days_to_expiry = self._days_until(registry_item["expiry_date"]) if registry_item.get("expiry_date") else None
            if days_to_expiry is None or days_to_expiry > within_days:
                continue
            item = {
                "source": "supplier_registry",
                "supplier_id": registry_item["id"],
                "supplier_name": registry_item["supplier_name"],
                "supplier_tin": registry_item["supplier_tin"],
                "certificate_ref": registry_item["certificate_ref"],
                "certificate_status": registry_item["certificate_status"],
                "days_to_expiry": days_to_expiry,
                "risk_level": registry_item["risk_level"],
            }
            items.append(item)
            seen_keys.add(key)

        for official in self.repo.list_halal_directory():
            key = official.get("certificate_ref") or official.get("company_tin")
            if key in seen_keys:
                continue
            days_to_expiry = self._days_until(official["expiry_date"])
            if days_to_expiry > within_days:
                continue
            items.append(
                {
                    "source": "halal_directory",
                    "supplier_id": None,
                    "supplier_name": official["company_name"],
                    "supplier_tin": official["company_tin"],
                    "certificate_ref": official["certificate_ref"],
                    "certificate_status": official["status"],
                    "days_to_expiry": days_to_expiry,
                    "risk_level": self._risk_level_for_certificate(
                        status=str(official["status"]),
                        expiry_date=official["expiry_date"],
                    ),
                }
            )

        items.sort(key=lambda item: (item["days_to_expiry"], item["supplier_name"] or ""))
        return self._envelope(
            status="success",
            source_system=self.settings.halal_source_system,
            next_action="halal.suppliers.upsert" if items else None,
            data={"within_days": within_days, "items": items},
        )

    def halal_workflows_create(self, payload: dict[str, Any]) -> dict[str, Any]:
        applicant_name = payload.get("applicant_name")
        product_name = payload.get("product_name")
        scheme = payload.get("scheme") or "food_and_beverage"
        framework = (payload.get("framework") or self._default_halal_framework(payload.get("company_size"))).upper()
        if not applicant_name or not product_name:
            raise InputError("applicant_name and product_name are required.")
        if framework not in HALAL_FRAMEWORK_RULES:
            raise InputError("framework must be IHCS or HAS.")

        workflow_id = str(uuid.uuid4())
        pack_id = payload.get("pack_id")
        bom_graph_id = payload.get("bom_graph_id")
        checklist_id = payload.get("checklist_id")
        completed_items = {
            "supplier_registry": bool(payload.get("supplier_registry_ready")),
            "bom_graph": bool(bom_graph_id),
            "evidence_pack": bool(pack_id),
            "checklist": bool(checklist_id),
            "internal_review": bool(payload.get("internal_review_ready")),
        }
        current_stage = self._workflow_stage_for_completed_items(completed_items)
        workflow_status = "ready_for_submission" if current_stage == "ready_for_submission" else "active"
        timestamp = now_iso()
        workflow_payload = {
            "applicant_name": applicant_name,
            "product_name": product_name,
            "scheme": scheme,
            "framework": framework,
            "company_size": payload.get("company_size"),
            "owners": payload.get("owners") or [],
            "linked_artifacts": {
                "pack_id": pack_id,
                "bom_graph_id": bom_graph_id,
                "checklist_id": checklist_id,
            },
            "completed_items": completed_items,
            "stages": HALAL_WORKFLOW_STAGES,
        }
        self.repo.create_halal_workflow(
            {
                "id": workflow_id,
                "applicant_name": applicant_name,
                "product_name": product_name,
                "scheme": scheme,
                "framework": framework,
                "current_stage": current_stage,
                "workflow_status": workflow_status,
                "source_system": self.settings.halal_source_system,
                "payload_json": workflow_payload,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        )
        return self._envelope(
            status="success",
            source_system=self.settings.halal_source_system,
            next_action="halal.workflows.status",
            data={
                "workflow_id": workflow_id,
                "workflow_status": workflow_status,
                "current_stage": current_stage,
                "completed_items": completed_items,
            },
            resource_id=workflow_id,
        )

    def halal_workflows_status(self, payload: dict[str, Any]) -> dict[str, Any]:
        workflow_id = payload.get("workflow_id")
        if not workflow_id:
            raise InputError("workflow_id is required.")
        workflow = self.repo.get_halal_workflow(str(workflow_id))
        if not workflow:
            raise NotFoundError(f"Unknown workflow_id: {workflow_id}")

        payload_json = workflow["payload_json"]
        completed_items = payload_json["completed_items"]
        if isinstance(payload.get("completed_items"), dict):
            completed_items = {**completed_items, **payload["completed_items"]}
            current_stage = self._workflow_stage_for_completed_items(completed_items)
            workflow_status = "ready_for_submission" if current_stage == "ready_for_submission" else "active"
            payload_json["completed_items"] = completed_items
            self.repo.update_halal_workflow(
                str(workflow_id),
                current_stage=current_stage,
                workflow_status=workflow_status,
                payload_json=payload_json,
                updated_at=now_iso(),
            )
            workflow = self.repo.get_halal_workflow(str(workflow_id))
            payload_json = workflow["payload_json"]

        open_queries = self.repo.list_halal_audit_queries(workflow_id=str(workflow_id), workflow_status="open")
        next_action = self._next_workflow_action(payload_json["completed_items"], bool(open_queries))
        return self._envelope(
            status="success",
            source_system=self.settings.halal_source_system,
            next_action=next_action,
            data={
                "workflow_id": workflow["id"],
                "workflow_status": workflow["workflow_status"],
                "current_stage": workflow["current_stage"],
                "framework": workflow["framework"],
                "completed_items": payload_json["completed_items"],
                "open_audit_queries": len(open_queries),
                "linked_artifacts": payload_json["linked_artifacts"],
            },
            resource_id=workflow["id"],
        )

    def halal_checklists_evaluate(self, payload: dict[str, Any]) -> dict[str, Any]:
        applicant_name = payload.get("applicant_name")
        framework = (payload.get("framework") or self._default_halal_framework(payload.get("company_size"))).upper()
        if not applicant_name:
            raise InputError("applicant_name is required.")
        if framework not in HALAL_FRAMEWORK_RULES:
            raise InputError("framework must be IHCS or HAS.")

        required_controls = HALAL_FRAMEWORK_RULES[framework]
        completed_controls = payload.get("completed_controls") or []
        if not isinstance(completed_controls, list):
            raise InputError("completed_controls must be an array.")

        completed_set = {str(item) for item in completed_controls}
        missing_controls = [control for control in required_controls if control not in completed_set]
        score = round(((len(required_controls) - len(missing_controls)) / len(required_controls)) * 100, 2)
        checklist_id = str(uuid.uuid4())
        workflow_status = "ready" if not missing_controls else "blocked_missing_controls"
        checklist_payload = {
            "framework": framework,
            "required_controls": required_controls,
            "completed_controls": sorted(completed_set),
            "missing_controls": missing_controls,
            "score": score,
        }
        self.repo.create_halal_checklist(
            {
                "id": checklist_id,
                "applicant_name": applicant_name,
                "framework": framework,
                "workflow_status": workflow_status,
                "score": score,
                "source_system": self.settings.halal_source_system,
                "payload_json": checklist_payload,
                "created_at": now_iso(),
            }
        )
        return self._envelope(
            status="success" if not missing_controls else "blocked",
            source_system=self.settings.halal_source_system,
            next_action="halal.workflows.create" if not missing_controls else "close_halal_controls",
            blocking_reason="missing_halal_controls" if missing_controls else None,
            data={
                "checklist_id": checklist_id,
                "framework": framework,
                "workflow_status": workflow_status,
                "score": score,
                "missing_controls": missing_controls,
            },
            resource_id=checklist_id,
        )

    def halal_audits_create_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        workflow_id = payload.get("workflow_id")
        query_title = payload.get("query_title")
        query_text = payload.get("query_text")
        if not workflow_id or not query_title or not query_text:
            raise InputError("workflow_id, query_title, and query_text are required.")
        workflow = self.repo.get_halal_workflow(str(workflow_id))
        if not workflow:
            raise NotFoundError(f"Unknown workflow_id: {workflow_id}")

        query_id = str(uuid.uuid4())
        timestamp = now_iso()
        query_payload = {
            "query_text": query_text,
            "requested_documents": payload.get("requested_documents") or [],
            "due_date": payload.get("due_date"),
            "owner": payload.get("owner"),
        }
        self.repo.create_halal_audit_query(
            {
                "id": query_id,
                "workflow_id": str(workflow_id),
                "query_title": str(query_title),
                "workflow_status": "open",
                "severity": str(payload.get("severity") or "medium"),
                "source_system": self.settings.halal_source_system,
                "payload_json": query_payload,
                "response_json": None,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        )
        workflow_payload = workflow["payload_json"]
        workflow_payload["completed_items"]["internal_review"] = False
        self.repo.update_halal_workflow(
            str(workflow_id),
            current_stage="audit_queries",
            workflow_status="active",
            payload_json=workflow_payload,
            updated_at=now_iso(),
        )
        return self._envelope(
            status="success",
            source_system=self.settings.halal_source_system,
            next_action="halal.audits.respond_query",
            data={
                "query_id": query_id,
                "workflow_id": workflow_id,
                "workflow_status": "open",
                "severity": payload.get("severity") or "medium",
            },
            resource_id=query_id,
        )

    def halal_audits_respond_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        query_id = payload.get("query_id")
        response_summary = payload.get("response_summary")
        if not query_id or not response_summary:
            raise InputError("query_id and response_summary are required.")
        query = self.repo.get_halal_audit_query(str(query_id))
        if not query:
            raise NotFoundError(f"Unknown query_id: {query_id}")

        self.repo.update_halal_audit_query(
            str(query_id),
            workflow_status="resolved",
            response_json={
                "response_summary": response_summary,
                "attachments": payload.get("attachments") or [],
                "responded_at": now_iso(),
            },
            updated_at=now_iso(),
        )
        remaining_open = self.repo.list_halal_audit_queries(
            workflow_id=query["workflow_id"],
            workflow_status="open",
        )
        if query["workflow_id"] and not remaining_open:
            workflow = self.repo.get_halal_workflow(query["workflow_id"])
            if workflow:
                workflow_payload = workflow["payload_json"]
                workflow_payload["completed_items"]["internal_review"] = True
                current_stage = self._workflow_stage_for_completed_items(workflow_payload["completed_items"])
                workflow_status = "ready_for_submission" if current_stage == "ready_for_submission" else "active"
                self.repo.update_halal_workflow(
                    query["workflow_id"],
                    current_stage=current_stage,
                    workflow_status=workflow_status,
                    payload_json=workflow_payload,
                    updated_at=now_iso(),
                )

        resolved = self.repo.get_halal_audit_query(str(query_id))
        return self._envelope(
            status="success",
            source_system=self.settings.halal_source_system,
            next_action="halal.workflows.status",
            data={"query": resolved},
            resource_id=str(query_id),
        )

    def halal_documents_share(self, payload: dict[str, Any]) -> dict[str, Any]:
        share_target = payload.get("share_target")
        documents = payload.get("documents") or []
        if not share_target:
            raise InputError("share_target is required.")
        if not isinstance(documents, list) or not documents:
            raise InputError("documents must be a non-empty array.")

        share_id = str(uuid.uuid4())
        share_payload = {
            "workflow_id": payload.get("workflow_id"),
            "pack_id": payload.get("pack_id"),
            "dossier_id": payload.get("dossier_id"),
            "documents": documents,
            "recipients": payload.get("recipients") or [],
            "channel": payload.get("channel") or "secure_link",
            "note": payload.get("note"),
        }
        self.repo.create_halal_document_share(
            {
                "id": share_id,
                "workflow_id": payload.get("workflow_id"),
                "share_target": str(share_target),
                "workflow_status": "shared",
                "source_system": self.settings.halal_source_system,
                "payload_json": share_payload,
                "created_at": now_iso(),
            }
        )
        return self._envelope(
            status="success",
            source_system=self.settings.halal_source_system,
            next_action=None,
            data={"share_id": share_id, "share": share_payload},
            resource_id=share_id,
        )

    def halal_export_dossier_generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        applicant_name = payload.get("applicant_name")
        product_name = payload.get("product_name")
        target_markets = payload.get("target_markets") or []
        if not applicant_name or not product_name:
            raise InputError("applicant_name and product_name are required.")
        if not isinstance(target_markets, list) or not target_markets:
            raise InputError("target_markets must be a non-empty array.")

        supporting_documents = payload.get("supporting_documents") or []
        if not isinstance(supporting_documents, list):
            raise InputError("supporting_documents must be an array.")

        missing_documents = [
            document
            for document in HALAL_REQUIRED_SUPPORTING_DOCUMENTS
            if document not in supporting_documents
        ]
        dossier_id = str(uuid.uuid4())
        workflow_id = payload.get("workflow_id")
        linked_workflow = self.repo.get_halal_workflow(str(workflow_id)) if workflow_id else None
        payload_json = {
            "applicant_name": applicant_name,
            "product_name": product_name,
            "target_markets": target_markets,
            "supporting_documents": supporting_documents,
            "workflow_id": workflow_id,
            "market_matrix": [
                {"market": market, "status": "ready" if not missing_documents else "needs_review"}
                for market in target_markets
            ],
            "sections": [
                "company_profile",
                "product_scope",
                "ingredient_traceability",
                "supplier_certificates",
                "export_supporting_documents",
            ],
            "linked_workflow_status": linked_workflow["workflow_status"] if linked_workflow else None,
            "missing_documents": missing_documents,
        }
        workflow_status = "ready" if not missing_documents else "blocked_missing_evidence"
        self.repo.create_halal_export_dossier(
            {
                "id": dossier_id,
                "applicant_name": applicant_name,
                "product_name": product_name,
                "workflow_status": workflow_status,
                "source_system": self.settings.halal_source_system,
                "payload_json": payload_json,
                "created_at": now_iso(),
            }
        )
        return self._envelope(
            status="success" if workflow_status == "ready" else "blocked",
            source_system=self.settings.halal_source_system,
            next_action="halal.documents.share" if workflow_status == "ready" else "collect_missing_halal_evidence",
            blocking_reason="missing_halal_supporting_evidence" if missing_documents else None,
            data={
                "dossier_id": dossier_id,
                "workflow_status": workflow_status,
                "missing_documents": missing_documents,
                "market_matrix": payload_json["market_matrix"],
            },
            resource_id=dossier_id,
        )

    def halal_dashboard_snapshot(self, payload: dict[str, Any]) -> dict[str, Any]:
        limit = int(payload.get("limit") or 8)
        suppliers = self.repo.list_halal_suppliers()
        renewals = self.halal_renewals_list({"within_days": payload.get("within_days") or 180})["data"]["items"]
        workflows = self.repo.list_halal_workflows(limit=limit)
        graphs = self.repo.list_halal_bom_graphs(limit=limit)
        packs = self.repo.list_halal_packs(limit=limit)
        checklists = self.repo.list_halal_checklists(limit=limit)
        audit_queries = self.repo.list_halal_audit_queries()
        shares = self.repo.list_halal_document_shares(limit=limit)
        dossiers = self.repo.list_halal_export_dossiers(limit=limit)

        summary = {
            "supplier_registry_total": len(suppliers),
            "active_supplier_certificates": len([item for item in suppliers if item["certificate_status"] == "active"]),
            "renewals_due_within_window": len(renewals),
            "workflows_total": len(workflows),
            "workflows_ready_for_submission": len([item for item in workflows if item["workflow_status"] == "ready_for_submission"]),
            "open_audit_queries": len([item for item in audit_queries if item["workflow_status"] == "open"]),
            "evidence_packs_total": len(packs),
            "export_dossiers_total": len(dossiers),
            "document_shares_total": len(shares),
        }

        recent_artifacts = {
            "suppliers": suppliers[:limit],
            "renewals": renewals[:limit],
            "workflows": workflows[:limit],
            "bom_graphs": [
                {
                    "id": item["id"],
                    "applicant_name": item["applicant_name"],
                    "product_name": item["product_name"],
                    "workflow_status": item["workflow_status"],
                    "summary": item["payload_json"]["summary"],
                    "nodes": item["payload_json"].get("nodes", []),
                    "edges": item["payload_json"].get("edges", []),
                    "issues": item["payload_json"].get("issues", []),
                    "bom": item["payload_json"].get("bom", []),
                    "updated_at": item["updated_at"],
                }
                for item in graphs[:limit]
            ],
            "evidence_packs": [
                {
                    "id": item["id"],
                    "applicant_name": item["applicant_name"],
                    "workflow_status": item["workflow_status"],
                    "product_name": item["payload_json"]["product_name"],
                    "missing_documents": item["payload_json"]["missing_documents"],
                    "supplier_gaps": item["payload_json"]["supplier_gaps"],
                    "created_at": item["created_at"],
                }
                for item in packs[:limit]
            ],
            "checklists": [
                {
                    "id": item["id"],
                    "applicant_name": item["applicant_name"],
                    "framework": item["framework"],
                    "workflow_status": item["workflow_status"],
                    "score": item["score"],
                    "missing_controls": item["payload_json"]["missing_controls"],
                    "created_at": item["created_at"],
                }
                for item in checklists[:limit]
            ],
            "audit_queries": audit_queries[:limit],
            "document_shares": shares[:limit],
            "export_dossiers": [
                {
                    "id": item["id"],
                    "applicant_name": item["applicant_name"],
                    "product_name": item["product_name"],
                    "workflow_status": item["workflow_status"],
                    "target_markets": item["payload_json"]["target_markets"],
                    "created_at": item["created_at"],
                }
                for item in dossiers[:limit]
            ],
        }

        return self._envelope(
            status="success",
            source_system=self.settings.halal_source_system,
            next_action="halal.pilot.seed_fnb" if not workflows else None,
            data={
                "summary": summary,
                "pilot_profile": HALAL_FNB_PILOT_DATASET,
                "recent_artifacts": recent_artifacts,
            },
        )

    def halal_pilot_seed_fnb(self, payload: dict[str, Any]) -> dict[str, Any]:
        pilot = HALAL_FNB_PILOT_DATASET
        applicant = pilot["applicant"]

        seeded_supplier_ids = []
        for supplier in pilot["suppliers"]:
            result = self.halal_suppliers_upsert(supplier)
            seeded_supplier_ids.append(result["resource_id"])

        graph = self.halal_bom_graph_generate(
            {
                "applicant_name": applicant["name"],
                "product_name": applicant["product_name"],
                "bom": pilot["bom"],
            }
        )
        graph_id = graph["data"]["graph_id"]

        checklist = self.halal_checklists_evaluate(
            {
                "applicant_name": applicant["name"],
                "framework": applicant["framework"],
                "company_size": applicant["company_size"],
                "completed_controls": applicant["completed_controls"],
            }
        )
        checklist_id = checklist["data"]["checklist_id"]

        pack = self.halal_evidence_pack_generate(
            {
                "applicant_name": applicant["name"],
                "product_name": applicant["product_name"],
                "bom": pilot["bom"],
                "supporting_documents": applicant["supporting_documents"],
            }
        )
        pack_id = pack["data"]["pack_id"]

        workflow = self.halal_workflows_create(
            {
                "applicant_name": applicant["name"],
                "product_name": applicant["product_name"],
                "scheme": applicant["scheme"],
                "framework": applicant["framework"],
                "company_size": applicant["company_size"],
                "supplier_registry_ready": True,
                "bom_graph_id": graph_id,
                "pack_id": pack_id,
                "checklist_id": checklist_id,
            }
        )
        workflow_id = workflow["data"]["workflow_id"]

        audit_query = self.halal_audits_create_query(
            {
                "workflow_id": workflow_id,
                **pilot["audit_query"],
            }
        )
        query_id = audit_query["data"]["query_id"]

        audit_response = self.halal_audits_respond_query(
            {
                "query_id": query_id,
                **pilot["audit_response"],
            }
        )

        workflow_status = self.halal_workflows_status({"workflow_id": workflow_id})

        dossier = self.halal_export_dossier_generate(
            {
                "workflow_id": workflow_id,
                "applicant_name": applicant["name"],
                "product_name": applicant["product_name"],
                "target_markets": applicant["target_markets"],
                "supporting_documents": applicant["supporting_documents"],
            }
        )
        dossier_id = dossier["data"]["dossier_id"]

        share = self.halal_documents_share(
            {
                "workflow_id": workflow_id,
                "dossier_id": dossier_id,
                **pilot["document_share"],
            }
        )

        snapshot = self.halal_dashboard_snapshot({})
        return self._envelope(
            status="success",
            source_system=self.settings.halal_source_system,
            next_action="halal.dashboard.snapshot",
            data={
                "pilot_id": pilot["pilot_id"],
                "sector": pilot["sector"],
                "seeded_supplier_ids": seeded_supplier_ids,
                "graph_id": graph_id,
                "checklist_id": checklist_id,
                "pack_id": pack_id,
                "workflow_id": workflow_id,
                "query_id": query_id,
                "audit_response_id": audit_response["resource_id"],
                "dossier_id": dossier_id,
                "share_id": share["resource_id"],
                "workflow_status": workflow_status["data"]["workflow_status"],
                "snapshot": snapshot["data"],
            },
        )

    def provider_myinvois_login(self, payload: dict[str, Any]) -> dict[str, Any]:
        environment = payload.get("environment") or self.settings.myinvois_default_env
        mode = (payload.get("mode") or "taxpayer").strip().lower()
        client = MyInvoisClient(self.settings, environment=environment)
        client_id, client_secret = client.default_credentials()
        client_id = payload.get("client_id") or client_id
        client_secret = payload.get("client_secret") or client_secret
        scope = payload.get("scope") or "InvoicingAPI"
        if not client_id or not client_secret:
            return self._envelope(
                status="blocked",
                source_system="myinvois_real",
                next_action="supply_myinvois_credentials",
                blocking_reason="missing_myinvois_credentials",
                data={"environment": client.environment, "mode": mode},
            )
        try:
            if mode == "intermediary":
                onbehalfof = payload.get("onbehalfof")
                if not onbehalfof:
                    raise InputError("onbehalfof is required for intermediary mode.")
                response = client.login_intermediary(
                    client_id=client_id,
                    client_secret=client_secret,
                    onbehalfof=str(onbehalfof),
                    scope=str(scope),
                )
            else:
                response = client.login_taxpayer(
                    client_id=client_id,
                    client_secret=client_secret,
                    scope=str(scope),
                )
        except RemoteApiError as exc:
            return self._provider_error_envelope(
                source_system="myinvois_real",
                exc=exc,
                next_action="check_credentials_or_portal_registration",
            )
        return self._envelope(
            status="success",
            source_system="myinvois_real",
            next_action="providers.myinvois.document_types",
            data={
                "environment": client.environment,
                "mode": mode,
                "auth": response,
                "api_base": client.api_base,
                "identity_base": client.identity_base,
            },
        )

    def provider_myinvois_document_types(self, payload: dict[str, Any]) -> dict[str, Any]:
        client, access_token = self._myinvois_client_and_token(payload)
        try:
            response = client.get_document_types(access_token=access_token)
        except RemoteApiError as exc:
            return self._provider_error_envelope(source_system="myinvois_real", exc=exc)
        return self._envelope(
            status="success",
            source_system="myinvois_real",
            data={"environment": client.environment, "document_types": response},
        )

    def provider_myinvois_validate_tin(self, payload: dict[str, Any]) -> dict[str, Any]:
        tin = payload.get("tin")
        id_type = payload.get("id_type")
        id_value = payload.get("id_value")
        if not tin or not id_type or not id_value:
            raise InputError("tin, id_type, and id_value are required.")
        client, access_token = self._myinvois_client_and_token(payload)
        try:
            response = client.validate_tin(
                access_token=access_token,
                tin=str(tin),
                id_type=str(id_type),
                id_value=str(id_value),
            )
        except RemoteApiError as exc:
            return self._provider_error_envelope(source_system="myinvois_real", exc=exc)
        return self._envelope(
            status="success",
            source_system="myinvois_real",
            data={
                "environment": client.environment,
                "validation": response,
            },
            resource_id=str(tin),
        )

    def provider_myinvois_search_tin(self, payload: dict[str, Any]) -> dict[str, Any]:
        id_type = payload.get("id_type")
        id_value = payload.get("id_value")
        if not id_type or not id_value:
            raise InputError("id_type and id_value are required.")
        entity_type = payload.get("entity_type")
        client, access_token = self._myinvois_client_and_token(payload)
        try:
            response = client.search_tin(
                access_token=access_token,
                id_type=str(id_type),
                id_value=str(id_value),
                entity_type=str(entity_type) if entity_type else None,
            )
        except RemoteApiError as exc:
            return self._provider_error_envelope(source_system="myinvois_real", exc=exc)
        return self._envelope(
            status="success",
            source_system="myinvois_real",
            data={
                "environment": client.environment,
                "search_result": response,
            },
        )

    def provider_myinvois_submit_documents(self, payload: dict[str, Any]) -> dict[str, Any]:
        documents = payload.get("documents")
        if not isinstance(documents, list) or not documents:
            raise InputError("documents must be a non-empty array.")
        client, access_token = self._myinvois_client_and_token(payload)
        try:
            response = client.submit_documents(access_token=access_token, documents=documents)
        except RemoteApiError as exc:
            return self._provider_error_envelope(source_system="myinvois_real", exc=exc)
        return self._envelope(
            status="success",
            source_system="myinvois_real",
            next_action="providers.myinvois.get_submission",
            data={
                "environment": client.environment,
                "submission": response,
            },
        )

    def provider_myinvois_get_submission(self, payload: dict[str, Any]) -> dict[str, Any]:
        submission_uid = payload.get("submission_uid")
        if not submission_uid:
            raise InputError("submission_uid is required.")
        page_no = int(payload.get("page_no") or 1)
        page_size = int(payload.get("page_size") or 100)
        client, access_token = self._myinvois_client_and_token(payload)
        try:
            response = client.get_submission(
                access_token=access_token,
                submission_uid=str(submission_uid),
                page_no=page_no,
                page_size=page_size,
            )
        except RemoteApiError as exc:
            return self._provider_error_envelope(source_system="myinvois_real", exc=exc)
        return self._envelope(
            status="success",
            source_system="myinvois_real",
            data={
                "environment": client.environment,
                "submission_uid": submission_uid,
                "submission": response,
            },
            resource_id=str(submission_uid),
        )

    def provider_myinvois_cancel_document(self, payload: dict[str, Any]) -> dict[str, Any]:
        document_uuid = payload.get("document_uuid")
        reason = payload.get("reason")
        if not document_uuid or not reason:
            raise InputError("document_uuid and reason are required.")
        client, access_token = self._myinvois_client_and_token(payload)
        try:
            response = client.cancel_document(
                access_token=access_token,
                document_uuid=str(document_uuid),
                reason=str(reason),
            )
        except RemoteApiError as exc:
            return self._provider_error_envelope(source_system="myinvois_real", exc=exc)
        return self._envelope(
            status="success",
            source_system="myinvois_real",
            data={
                "environment": client.environment,
                "document_uuid": document_uuid,
                "cancel_result": response,
            },
            resource_id=str(document_uuid),
        )

    def provider_cidb_states(self, payload: dict[str, Any]) -> dict[str, Any]:
        client, access_token = self._cidb_client_and_token(payload)
        if not access_token:
            return self._envelope(
                status="blocked",
                source_system="cidb_real",
                next_action="supply_cidb_access_token",
                blocking_reason="missing_cidb_access_token",
                data={},
            )
        try:
            states = client.get_states(access_token=access_token)
        except RemoteApiError as exc:
            return self._provider_error_envelope(source_system="cidb_real", exc=exc)
        state_code = payload.get("state_code")
        if state_code:
            filtered = [item for item in states if str(item.get("code", "")).upper() == str(state_code).upper()]
        else:
            filtered = states
        return self._envelope(
            status="success",
            source_system="cidb_real",
            data={"states": filtered},
        )

    def provider_cidb_labour_wage_rate(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._cidb_state_dataset(
            payload=payload,
            fetcher_name="get_labour_wage_rate",
            result_key="labour_wage_rate",
        )

    def provider_cidb_building_material_price(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._cidb_state_dataset(
            payload=payload,
            fetcher_name="get_building_material_price",
            result_key="building_material_price",
        )

    def provider_cidb_machinery_rates(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._cidb_state_dataset(
            payload=payload,
            fetcher_name="get_machinery_rates",
            result_key="machinery_rates",
        )

    def _normalize_invoice(self, payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        required_fields = ["invoice_number", "issue_date", "supplier_tin", "buyer_tin", "line_items"]
        errors = [f"missing_{field}" for field in required_fields if not payload.get(field)]

        supplier = self.repo.get_entity_by_tin(str(payload.get("supplier_tin", ""))) if payload.get("supplier_tin") else None
        buyer = self.repo.get_entity_by_tin(str(payload.get("buyer_tin", ""))) if payload.get("buyer_tin") else None
        if payload.get("supplier_tin") and (not supplier or not supplier["tax_active"]):
            errors.append("invalid_supplier_tin")
        if payload.get("buyer_tin") and (not buyer or not buyer["tax_active"]):
            errors.append("invalid_buyer_tin")

        line_items = payload.get("line_items") or []
        if not isinstance(line_items, list):
            errors.append("line_items_must_be_array")
            line_items = []

        normalized_items = []
        calculated_total = Decimal("0.00")
        for index, item in enumerate(line_items):
            if not isinstance(item, dict):
                errors.append(f"line_item_{index}_must_be_object")
                continue
            description = item.get("description")
            quantity = item.get("quantity")
            unit_price = item.get("unit_price")
            if description in (None, ""):
                errors.append(f"line_item_{index}_missing_description")
            if quantity in (None, ""):
                errors.append(f"line_item_{index}_missing_quantity")
            if unit_price in (None, ""):
                errors.append(f"line_item_{index}_missing_unit_price")
            if quantity in (None, "") or unit_price in (None, ""):
                continue
            line_total = Decimal(str(quantity)) * Decimal(str(unit_price))
            line_total = line_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            calculated_total += line_total
            normalized_items.append(
                {
                    "description": description,
                    "quantity": quantity,
                    "unit_price": as_money(unit_price),
                    "line_total": float(line_total),
                }
            )

        provided_total = payload.get("total_amount")
        total_amount = as_money(provided_total) if provided_total is not None else float(calculated_total)
        if normalized_items and Decimal(str(total_amount)) != calculated_total:
            errors.append("invoice_total_mismatch")

        normalized = {
            "invoice_number": payload.get("invoice_number"),
            "issue_date": payload.get("issue_date"),
            "supplier_tin": payload.get("supplier_tin"),
            "buyer_tin": payload.get("buyer_tin"),
            "currency": payload.get("currency") or self.settings.default_currency,
            "line_items": normalized_items,
            "line_items_count": len(normalized_items),
            "total_amount": total_amount,
        }
        return normalized, errors

    def _build_duitnow_request(self, *, reference: str, amount: float) -> str:
        merchant = quote(self.settings.merchant_name, safe="")
        return (
            f"duitnow://sandbox/request/{reference}"
            f"?merchant_id={quote(self.settings.merchant_duitnow_id, safe='')}"
            f"&merchant_name={merchant}"
            f"&amount={amount:.2f}"
            f"&currency={self.settings.default_currency}"
            f"&city={quote(self.settings.merchant_city, safe='')}"
        )

    def _canonical_action_name(self, action: Any) -> str | None:
        if not action:
            return None
        raw = str(action).strip()
        return self.ACTION_ALIASES.get(raw, raw)

    def _maybe_block_for_approval(self, action: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        if action in self.READ_ONLY_ACTIONS or action.startswith("approvals.") or action.startswith("workflows."):
            return None
        policy = self._approval_policy_for_action(action, payload)
        if not policy:
            return None

        approval_id = payload.get("approval_id")
        if approval_id:
            approval = self.repo.get_approval(str(approval_id))
            if not approval or approval["action"] != action:
                return self._envelope(
                    status="blocked",
                    source_system="approval_store",
                    next_action="approvals.approve",
                    blocking_reason="invalid_approval_reference",
                    data={"approval_id": approval_id, "action": action},
                )
            if approval["workflow_status"] == "approved":
                return None
            if approval["workflow_status"] == "rejected":
                return self._envelope(
                    status="blocked",
                    source_system="approval_store",
                    next_action=None,
                    blocking_reason="approval_rejected",
                    data={"approval": approval},
                    resource_id=str(approval_id),
                )
            return self._envelope(
                status="blocked",
                source_system="approval_store",
                next_action="approvals.approve",
                blocking_reason="awaiting_human_approval",
                data={"approval": approval, "approval_id": approval["id"]},
                resource_id=str(approval["id"]),
            )

        created = self._create_approval_request(action=action, payload=payload, policy=policy)
        return self._envelope(
            status="blocked",
            source_system="approval_store",
            next_action="approvals.approve",
            blocking_reason="awaiting_human_approval",
            data={"approval": created, "approval_id": created["id"]},
            resource_id=created["id"],
        )

    def _approval_policy_for_action(self, action: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        if action in {"invoices.submit", "providers.myinvois.submit_documents"} and self._invoice_execution_mode(payload) == "real":
            return {
                "policy_key": "myinvois.real_submission",
                "reason": "Real MyInvois submission requires explicit delegated approval.",
                "target_resource_type": "invoice",
                "target_resource_id": payload.get("invoice_number") or payload.get("resource_id"),
            }
        if action in {"invoices.cancel", "providers.myinvois.cancel_document"}:
            if action == "providers.myinvois.cancel_document" or payload.get("provider") in {"real", "myinvois_real"}:
                return {
                    "policy_key": "myinvois.real_cancellation",
                    "reason": "Real document cancellation requires explicit delegated approval.",
                    "target_resource_type": "invoice_submission",
                    "target_resource_id": payload.get("submission_id") or payload.get("document_uuid"),
                }
        if action == "payments.create_request":
            amount = payload.get("amount")
            if amount is None and payload.get("submission_id"):
                submission = self.repo.get_invoice_submission(str(payload["submission_id"]))
                if submission:
                    amount = submission.get("total_amount")
            if amount is not None and as_money(amount) >= self.settings.approval_payment_threshold:
                return {
                    "policy_key": "payments.request.threshold",
                    "reason": "Payment request exceeds the auto-execution threshold.",
                    "target_resource_type": "invoice_submission",
                    "target_resource_id": payload.get("submission_id"),
                }
        return None

    def _create_approval_request(self, *, action: str, payload: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
        approval_id = str(uuid.uuid4())
        timestamp = now_iso()
        record = {
            "id": approval_id,
            "action": action,
            "target_resource_type": policy.get("target_resource_type"),
            "target_resource_id": str(policy.get("target_resource_id")) if policy.get("target_resource_id") else None,
            "policy_key": policy["policy_key"],
            "workflow_status": "pending",
            "reason": policy["reason"],
            "requested_payload_json": self._redacted_payload_for_audit(payload),
            "approval_context_json": None,
            "decision_context_json": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        self.repo.create_approval(record)
        return self.repo.get_approval(approval_id) or record

    @staticmethod
    def _redacted_payload_for_audit(payload: dict[str, Any]) -> dict[str, Any]:
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            if key in {"client_secret", "access_token", "authorization"}:
                redacted[key] = "***"
            elif isinstance(value, dict):
                redacted[key] = OperationsService._redacted_payload_for_audit(value)
            else:
                redacted[key] = value
        return redacted

    def _invoice_execution_mode(self, payload: dict[str, Any]) -> str:
        declared = str(payload.get("provider") or payload.get("execution_mode") or "auto").strip().lower()
        if declared in {"sandbox", "local"}:
            return "sandbox"
        if declared in {"real", "myinvois_real"}:
            return "real"
        if payload.get("documents") and (
            payload.get("access_token")
            or self.settings.myinvois_access_token
            or payload.get("client_id")
            or self.settings.myinvois_sandbox_client_id
            or self.settings.myinvois_production_client_id
        ):
            return "real"
        return "sandbox"

    def _submit_invoice_real(self, payload: dict[str, Any]) -> dict[str, Any]:
        documents = payload.get("documents")
        if not isinstance(documents, list) or not documents:
            return self._envelope(
                status="blocked",
                source_system="myinvois_real",
                next_action="provide_myinvois_documents_payload",
                blocking_reason="missing_myinvois_documents",
                data={"expected_field": "documents"},
                resource_id=str(payload.get("invoice_number") or "unknown"),
            )
        try:
            client, access_token = self._myinvois_client_and_token_for_execution(payload)
            response = client.submit_documents(access_token=access_token, documents=documents)
        except RemoteApiError as exc:
            return self._provider_error_envelope(
                source_system="myinvois_real",
                exc=exc,
                next_action="check_credentials_or_portal_registration",
            )
        except InputError as exc:
            return self._envelope(
                status="blocked",
                source_system="myinvois_real",
                next_action="supply_myinvois_credentials",
                blocking_reason="missing_myinvois_credentials",
                data={"error": str(exc)},
                resource_id=str(payload.get("invoice_number") or "unknown"),
            )

        submission_id = str(uuid.uuid4())
        timestamp = now_iso()
        accepted_documents = response.get("acceptedDocuments") or []
        rejected_documents = response.get("rejectedDocuments") or []
        external_submission_id = response.get("submissionUID")
        external_document_id = accepted_documents[0].get("uuid") if accepted_documents else None
        workflow_status = "submitted" if accepted_documents else "invalid"
        next_action = "invoices.status" if accepted_documents else "exceptions.resolve"
        blocking_reason = None if accepted_documents else "remote_document_rejected"
        if rejected_documents:
            self._create_exception(
                exception_type="myinvois_remote_rejection",
                resource_type="invoice_submission",
                resource_id=submission_id,
                summary="MyInvois rejected one or more submitted documents.",
                source_system="myinvois_real",
                details={"response": response},
                severity="high",
            )
        self.repo.create_invoice_submission(
            {
                "id": submission_id,
                "invoice_number": str(payload.get("invoice_number") or accepted_documents[0].get("invoiceCodeNumber") if accepted_documents else "unknown"),
                "supplier_tin": str(payload.get("supplier_tin") or ""),
                "buyer_tin": str(payload.get("buyer_tin") or ""),
                "currency": str(payload.get("currency") or self.settings.default_currency),
                "total_amount": as_money(payload.get("total_amount") or 0),
                "workflow_status": workflow_status,
                "source_system": "myinvois_real",
                "next_action": next_action,
                "blocking_reason": blocking_reason,
                "poll_count": 0,
                "external_submission_id": external_submission_id,
                "external_document_id": external_document_id,
                "payload_json": {
                    "execution_mode": "real",
                    "environment": client.environment,
                    "documents": documents,
                    "request": self._redacted_payload_for_audit(payload),
                },
                "validation_json": response,
                "created_at": timestamp,
                "updated_at": timestamp,
                "canceled_at": None,
            }
        )
        return self._envelope(
            status="success" if accepted_documents else "blocked",
            source_system="myinvois_real",
            next_action=next_action,
            blocking_reason=blocking_reason,
            data={
                "submission_id": submission_id,
                "submission_status": workflow_status,
                "execution_mode": "real",
                "environment": client.environment,
                "remote_submission": response,
            },
            resource_id=submission_id,
        )

    def _invoice_status_real(self, payload: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
        try:
            client, access_token = self._myinvois_client_and_token_for_execution(
                {
                    **(submission.get("payload_json") or {}),
                    **payload,
                }
            )
            response = client.get_submission(
                access_token=access_token,
                submission_uid=str(submission["external_submission_id"]),
                page_no=int(payload.get("page_no") or 1),
                page_size=int(payload.get("page_size") or 100),
            )
        except RemoteApiError as exc:
            return self._provider_error_envelope(source_system="myinvois_real", exc=exc)
        except InputError as exc:
            return self._envelope(
                status="blocked",
                source_system="myinvois_real",
                next_action="supply_myinvois_credentials",
                blocking_reason="missing_myinvois_credentials",
                data={"error": str(exc)},
                resource_id=submission["id"],
            )

        workflow_status, next_action, blocking_reason, external_document_id = self._map_myinvois_submission_state(response)
        self.repo.update_invoice_submission(
            submission["id"],
            workflow_status=workflow_status,
            next_action=next_action,
            blocking_reason=blocking_reason,
            poll_count=submission["poll_count"] + 1,
            external_document_id=external_document_id or submission["external_document_id"],
            validation_json=response,
            updated_at=now_iso(),
        )
        refreshed = self.repo.get_invoice_submission(submission["id"]) or submission
        if workflow_status == "invalid":
            self._create_exception(
                exception_type="myinvois_submission_invalid",
                resource_type="invoice_submission",
                resource_id=refreshed["id"],
                summary="MyInvois reported the submission as invalid.",
                source_system="myinvois_real",
                details={"submission": response},
            )
        envelope_status = "success"
        if blocking_reason:
            envelope_status = "blocked"
        return self._envelope(
            status=envelope_status,
            source_system="myinvois_real",
            next_action=next_action,
            blocking_reason=blocking_reason,
            data={
                "submission_id": refreshed["id"],
                "submission_status": refreshed["workflow_status"],
                "external_submission_id": refreshed["external_submission_id"],
                "external_document_id": refreshed["external_document_id"],
                "poll_count": refreshed["poll_count"],
                "remote_submission": response,
            },
            resource_id=refreshed["id"],
        )

    def _cancel_invoice_real(self, payload: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
        document_uuid = payload.get("document_uuid") or submission.get("external_document_id")
        reason = payload.get("reason")
        if not document_uuid or not reason:
            raise InputError("reason and an external document UUID are required for real cancellation.")
        try:
            client, access_token = self._myinvois_client_and_token_for_execution(
                {
                    **(submission.get("payload_json") or {}),
                    **payload,
                }
            )
            response = client.cancel_document(
                access_token=access_token,
                document_uuid=str(document_uuid),
                reason=str(reason),
            )
        except RemoteApiError as exc:
            return self._provider_error_envelope(source_system="myinvois_real", exc=exc)
        except InputError as exc:
            return self._envelope(
                status="blocked",
                source_system="myinvois_real",
                next_action="supply_myinvois_credentials",
                blocking_reason="missing_myinvois_credentials",
                data={"error": str(exc)},
                resource_id=submission["id"],
            )
        self.repo.update_invoice_submission(
            submission["id"],
            workflow_status="canceled",
            next_action=None,
            blocking_reason=None,
            canceled_at=now_iso(),
            validation_json=response,
            updated_at=now_iso(),
        )
        return self._envelope(
            status="success",
            source_system="myinvois_real",
            data={
                "submission_id": submission["id"],
                "submission_status": "canceled",
                "cancel_result": response,
            },
            resource_id=submission["id"],
        )

    def _map_myinvois_submission_state(self, response: dict[str, Any]) -> tuple[str, str | None, str | None, str | None]:
        overall_status = str(response.get("overallStatus") or "").strip().lower()
        document_summary = response.get("documentSummary") or []
        primary_status = str(document_summary[0].get("status") if document_summary else overall_status).strip().lower()
        external_document_id = document_summary[0].get("uuid") if document_summary else None
        if overall_status in {"in progress"} or primary_status in {"submitted"}:
            return "submitted", "invoices.status", "awaiting_remote_processing", external_document_id
        if primary_status in {"valid"} or overall_status in {"valid"}:
            return "validated", "payments.create_request", None, external_document_id
        if primary_status in {"cancelled", "canceled"}:
            return "canceled", None, None, external_document_id
        if primary_status in {"invalid"} or overall_status in {"invalid", "partially valid"}:
            return "invalid", "exceptions.resolve", "remote_document_invalid", external_document_id
        return "submitted", "invoices.status", "awaiting_remote_processing", external_document_id

    def _myinvois_client_and_token_for_execution(self, payload: dict[str, Any]) -> tuple[MyInvoisClient, str]:
        environment = payload.get("environment") or self.settings.myinvois_default_env
        access_token = payload.get("access_token") or self.settings.myinvois_access_token
        client = MyInvoisClient(self.settings, environment=environment)
        if access_token:
            return client, str(access_token)
        client_id, client_secret = client.default_credentials()
        client_id = payload.get("client_id") or client_id
        client_secret = payload.get("client_secret") or client_secret
        if not client_id or not client_secret:
            raise InputError("MyInvois access_token or client credentials are required.")
        mode = str(payload.get("mode") or "taxpayer").strip().lower()
        scope = str(payload.get("scope") or "InvoicingAPI")
        if mode == "intermediary":
            onbehalfof = payload.get("onbehalfof")
            if not onbehalfof:
                raise InputError("onbehalfof is required for intermediary mode.")
            auth = client.login_intermediary(
                client_id=str(client_id),
                client_secret=str(client_secret),
                onbehalfof=str(onbehalfof),
                scope=scope,
            )
        else:
            auth = client.login_taxpayer(
                client_id=str(client_id),
                client_secret=str(client_secret),
                scope=scope,
            )
        access_token = auth.get("access_token")
        if not access_token:
            raise InputError("Unable to obtain a MyInvois access token from the login response.")
        return client, str(access_token)

    def _derive_runner_payload(
        self,
        root_payload: dict[str, Any],
        current_action: str,
        current_payload: dict[str, Any],
        response: dict[str, Any],
        next_action: str,
    ) -> dict[str, Any] | None:
        carried = self._runner_carried_fields(root_payload)
        if next_action == "entities.verify_taxpayer":
            tin = response.get("data", {}).get("primary_match", {}).get("tin") or response.get("resource_id")
            return {"tin": tin, **carried} if tin else None
        if next_action == "invoices.submit":
            invoice_payload = root_payload.get("invoice") if isinstance(root_payload.get("invoice"), dict) else root_payload
            return {**invoice_payload, **carried} if invoice_payload else None
        if next_action == "invoices.status":
            submission_id = (
                response.get("data", {}).get("submission_id")
                or current_payload.get("submission_id")
                or response.get("resource_id")
            )
            return {"submission_id": submission_id, **carried} if submission_id else None
        if next_action == "payments.create_request":
            submission_id = (
                response.get("data", {}).get("submission_id")
                or current_payload.get("submission_id")
                or response.get("resource_id")
            )
            payment_payload = root_payload.get("payment") if isinstance(root_payload.get("payment"), dict) else {}
            return {"submission_id": submission_id, **payment_payload, **carried} if submission_id else None
        if next_action == "payments.ingest_event":
            event_payload = root_payload.get("payment_event")
            suggested = response.get("data", {}).get("suggested_event_payload")
            auto_settle = bool(root_payload.get("auto_settle"))
            base_payload = event_payload if isinstance(event_payload, dict) else (suggested if auto_settle else None)
            if not isinstance(base_payload, dict):
                return None
            return {
                **base_payload,
                "request_id": base_payload.get("request_id") or response.get("data", {}).get("request_id") or current_payload.get("request_id"),
                "reference": base_payload.get("reference") or response.get("data", {}).get("reference") or current_payload.get("reference"),
            }
        if next_action == "halal.dashboard.snapshot":
            return {}
        if next_action == "halal.workflows.status":
            workflow_id = response.get("data", {}).get("workflow_id") or response.get("resource_id")
            return {"workflow_id": workflow_id} if workflow_id else None
        return None

    @staticmethod
    def _runner_carried_fields(root_payload: dict[str, Any]) -> dict[str, Any]:
        carried_keys = {
            "provider",
            "execution_mode",
            "environment",
            "access_token",
            "client_id",
            "client_secret",
            "mode",
            "scope",
            "onbehalfof",
            "approval_id",
        }
        return {key: root_payload[key] for key in carried_keys if key in root_payload}

    @staticmethod
    def _entity_public(entity: dict[str, Any]) -> dict[str, Any]:
        return {
            "tin": entity["tin"],
            "registration_no": entity["registration_no"],
            "name": entity["name"],
            "industry": entity["industry"],
            "tax_active": bool(entity["tax_active"]),
            "business_registry_status": entity["business_registry_status"],
            "aliases": entity["aliases_json"],
        }

    def _resolve_halal_supplier(
        self,
        *,
        supplier_tin: Any = None,
        supplier_name: Any = None,
        certificate_ref: Any = None,
    ) -> dict[str, Any]:
        registry_record = None
        if supplier_tin:
            registry_record = self.repo.get_halal_supplier_by_tin(str(supplier_tin))

        official_record = self.repo.get_halal_status(
            certificate_ref=str(certificate_ref) if certificate_ref else None,
            company_tin=str(supplier_tin) if supplier_tin else None,
            company_name=str(supplier_name) if supplier_name else None,
        )

        candidate = official_record or registry_record or {}
        certificate_status = (
            candidate.get("status")
            or candidate.get("certificate_status")
            or "unknown"
        )
        expiry_date = candidate.get("expiry_date")
        days_to_expiry = self._days_until(expiry_date) if expiry_date else None
        supplier_profile = {
            "supplier_tin": supplier_tin or candidate.get("company_tin") or candidate.get("supplier_tin"),
            "supplier_name": supplier_name or candidate.get("company_name") or candidate.get("supplier_name"),
            "certificate_ref": certificate_ref or candidate.get("certificate_ref"),
            "certificate_status": certificate_status,
            "expiry_date": expiry_date,
            "days_to_expiry": days_to_expiry,
            "products": candidate.get("products_json") or candidate.get("products") or [],
            "risk_level": self._risk_level_for_certificate(
                status=str(certificate_status),
                expiry_date=expiry_date,
            ),
        }
        return {
            "registry_record": registry_record,
            "official_record": official_record,
            "supplier_profile": supplier_profile,
        }

    @staticmethod
    def _slug(value: str) -> str:
        cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
        while "--" in cleaned:
            cleaned = cleaned.replace("--", "-")
        return cleaned.strip("-") or "item"

    @staticmethod
    def _days_until(date_text: str | None) -> int | None:
        if not date_text:
            return None
        target = datetime.fromisoformat(str(date_text)).date()
        today = datetime.now(UTC).date()
        return (target - today).days

    def _risk_level_for_certificate(self, *, status: str, expiry_date: str | None) -> str:
        normalized_status = status.strip().lower()
        if normalized_status != "active":
            return "high"
        days_to_expiry = self._days_until(expiry_date) if expiry_date else None
        if days_to_expiry is None:
            return "medium"
        if days_to_expiry <= 90:
            return "medium"
        return "low"

    @staticmethod
    def _default_halal_framework(company_size: Any) -> str:
        normalized = str(company_size or "").strip().lower()
        if normalized in {"micro", "small", "sme"}:
            return "IHCS"
        return "HAS"

    @staticmethod
    def _workflow_stage_for_completed_items(completed_items: dict[str, bool]) -> str:
        if not completed_items.get("supplier_registry"):
            return "supplier_registry"
        if not completed_items.get("bom_graph"):
            return "ingredient_review"
        if not completed_items.get("evidence_pack"):
            return "evidence_assembly"
        if not completed_items.get("checklist"):
            return "internal_review"
        if not completed_items.get("internal_review"):
            return "audit_queries"
        return "ready_for_submission"

    @staticmethod
    def _next_workflow_action(completed_items: dict[str, bool], has_open_queries: bool) -> str | None:
        if not completed_items.get("supplier_registry"):
            return "halal.suppliers.upsert"
        if not completed_items.get("bom_graph"):
            return "halal.bom.graph.generate"
        if not completed_items.get("evidence_pack"):
            return "halal.evidence_pack.generate"
        if not completed_items.get("checklist"):
            return "halal.checklists.evaluate"
        if has_open_queries:
            return "halal.audits.respond_query"
        if not completed_items.get("internal_review"):
            return "halal.audits.create_query"
        return "halal.export_dossier.generate"

    def _myinvois_client_and_token(self, payload: dict[str, Any]) -> tuple[MyInvoisClient, str]:
        environment = payload.get("environment") or self.settings.myinvois_default_env
        access_token = payload.get("access_token") or self.settings.myinvois_access_token
        if not access_token:
            raise InputError("access_token is required.")
        return MyInvoisClient(self.settings, environment=environment), str(access_token)

    def _cidb_client_and_token(self, payload: dict[str, Any]) -> tuple[CIDBClient, str]:
        access_token = payload.get("access_token") or self.settings.cidb_access_token
        if not access_token:
            return CIDBClient(self.settings), ""
        return CIDBClient(self.settings), str(access_token)

    def _cidb_state_dataset(
        self,
        *,
        payload: dict[str, Any],
        fetcher_name: str,
        result_key: str,
    ) -> dict[str, Any]:
        client, access_token = self._cidb_client_and_token(payload)
        if not access_token:
            return self._envelope(
                status="blocked",
                source_system="cidb_real",
                next_action="supply_cidb_access_token",
                blocking_reason="missing_cidb_access_token",
                data={},
            )
        state_code = payload.get("state_code")
        if not state_code:
            raise InputError("state_code is required.")
        year = int(payload.get("year") or datetime.now(UTC).year)
        try:
            states = client.get_states(access_token=access_token)
            selected = next(
                (item for item in states if str(item.get("code", "")).upper() == str(state_code).upper()),
                None,
            )
            if not selected:
                return self._envelope(
                    status="blocked",
                    source_system="cidb_real",
                    next_action="providers.cidb.states",
                    blocking_reason="unknown_state_code",
                    data={"state_code": state_code},
                )
            fetcher = getattr(client, fetcher_name)
            dataset = fetcher(
                access_token=access_token,
                state_id=int(selected["id"]),
                state_name=str(selected["name"]),
                year=year,
            )
        except RemoteApiError as exc:
            return self._provider_error_envelope(source_system="cidb_real", exc=exc)
        return self._envelope(
            status="success",
            source_system="cidb_real",
            data={
                "state": selected,
                "year": year,
                result_key: dataset,
            },
            resource_id=str(selected["code"]),
        )
