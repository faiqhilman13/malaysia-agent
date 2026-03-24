from __future__ import annotations

import json
import sys
from typing import Any, TextIO

from .config import Settings
from .service import InputError, NotFoundError, OperationsService


PROTOCOL_VERSION = "2025-11-25"
SERVER_NAME = "malaysia-agent-ops"
SERVER_VERSION = "0.1.0"

COMMON_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string"},
        "next_action": {"type": ["string", "null"]},
        "blocking_reason": {"type": ["string", "null"]},
        "source_system": {"type": "string"},
        "resource_id": {"type": ["string", "null"]},
        "timestamp": {"type": "string"},
        "data": {"type": "object"},
    },
    "required": [
        "status",
        "next_action",
        "blocking_reason",
        "source_system",
        "resource_id",
        "timestamp",
        "data",
    ],
}

TOOL_DESCRIPTIONS = {
    "workflows.run": "Run an action chain automatically until it completes, blocks, or waits for an external event or human approval.",
    "workflows.status": "Retrieve the persisted state and execution log for a workflow run.",
    "approvals.list": "List pending, approved, or rejected approval requests for sensitive actions.",
    "approvals.approve": "Approve a pending action using a verified local identity context.",
    "approvals.reject": "Reject a pending sensitive action.",
    "entities.resolve": "Resolve a Malaysian business entity by query, TIN, registration number, or name.",
    "entities.verify_taxpayer": "Verify whether a taxpayer identifier is active and usable.",
    "entities.verify_business_registry": "Verify whether a business registry record is active.",
    "invoices.validate": "Validate a normalized invoice payload before submission.",
    "invoices.submit": "Submit an invoice through sandbox flow or the real MyInvois rail when configured.",
    "invoices.status": "Refresh invoice submission state from local sandbox state or real MyInvois status.",
    "invoices.cancel": "Cancel an invoice submission locally or through real MyInvois when configured.",
    "payments.create_request": "Create a payment request and return the event-driven settlement details for the request.",
    "payments.ingest_event": "Ingest an external payment event or webhook payload and update payment and invoice state automatically.",
    "payments.reconcile": "Manually reconcile a payment as an operator fallback.",
    "exceptions.list": "List open or resolved workflow exceptions.",
    "exceptions.resolve": "Resolve a workflow exception with an operator note.",
    "trade.doc_pack.validate": "Validate a trade or customs document pack against required document rules.",
    "trade.submission.status": "Read the current trade validation state.",
    "halal.status.lookup": "Look up a halal certificate or company status record.",
    "halal.evidence_pack.generate": "Generate a halal evidence pack from BOM and supporting documents.",
    "halal.suppliers.upsert": "Upsert a supplier into the halal supplier registry.",
    "halal.suppliers.list": "List suppliers in the halal supplier registry.",
    "halal.bom.graph.generate": "Generate a supplier, ingredient, and certificate dependency graph for a halal BOM.",
    "halal.renewals.list": "List halal supplier certificates nearing expiry.",
    "halal.workflows.create": "Create a halal workflow from evidence, checklist, and BOM prerequisites.",
    "halal.workflows.status": "Read the current halal workflow stage and next action.",
    "halal.checklists.evaluate": "Evaluate a halal control checklist against IHCS or HAS controls.",
    "halal.audits.create_query": "Create an audit or query item inside a halal workflow.",
    "halal.audits.respond_query": "Respond to a halal audit or query item.",
    "halal.documents.share": "Create a document share record for OEM, partner, or customer handoff.",
    "halal.export_dossier.generate": "Generate an export-ready halal dossier for target markets.",
    "halal.dashboard.snapshot": "Return the aggregated halal dashboard snapshot used by the operator UI.",
    "halal.pilot.seed_fnb": "Seed the F&B halal pilot dataset and generate linked workflow artifacts.",
    "providers.myinvois.login": "Authenticate against the official MyInvois identity endpoint.",
    "providers.myinvois.document_types": "List MyInvois document types and versions.",
    "providers.myinvois.validate_tin": "Validate a taxpayer TIN through MyInvois.",
    "providers.myinvois.search_tin": "Search a taxpayer TIN through MyInvois.",
    "providers.myinvois.submit_documents": "Submit UBL documents directly through MyInvois.",
    "providers.myinvois.get_submission": "Retrieve a MyInvois submission directly by submission UID.",
    "providers.myinvois.cancel_document": "Cancel a MyInvois document directly by UUID.",
    "providers.cidb.states": "List Malaysian states from CIDB N3C.",
    "providers.cidb.labour_wage_rate": "Fetch CIDB labour wage rate data for a state and year.",
    "providers.cidb.building_material_price": "Fetch CIDB building material prices for a state and year.",
    "providers.cidb.machinery_rates": "Fetch CIDB machinery rates for a state and year.",
}

TOOL_INPUT_SCHEMAS: dict[str, dict[str, Any]] = {
    "workflows.run": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "Root action to invoke."},
            "payload": {"type": "object", "description": "Initial payload for the root action."},
            "max_steps": {"type": "integer", "minimum": 1, "description": "Maximum automatic execution steps."},
        },
        "required": ["action"],
        "additionalProperties": False,
    },
    "workflows.status": {
        "type": "object",
        "properties": {
            "run_id": {"type": "string", "description": "Persisted workflow run identifier."},
        },
        "required": ["run_id"],
        "additionalProperties": False,
    },
    "approvals.approve": {
        "type": "object",
        "properties": {
            "approval_id": {"type": "string"},
            "identity": {
                "type": "object",
                "properties": {
                    "authority_id": {"type": "string"},
                    "authority_type": {"type": "string"},
                    "provider": {"type": "string"},
                    "verified": {"type": "boolean"},
                },
                "required": ["verified"],
                "additionalProperties": True,
            },
            "note": {"type": "string"},
        },
        "required": ["approval_id", "identity"],
        "additionalProperties": False,
    },
    "approvals.reject": {
        "type": "object",
        "properties": {
            "approval_id": {"type": "string"},
            "identity": {"type": "object"},
            "note": {"type": "string"},
        },
        "required": ["approval_id"],
        "additionalProperties": False,
    },
    "payments.ingest_event": {
        "type": "object",
        "properties": {
            "request_id": {"type": "string"},
            "reference": {"type": "string"},
            "event_type": {"type": "string"},
            "payment_status": {"type": "string"},
            "amount": {"type": "number"},
            "currency": {"type": "string"},
            "external_reference": {"type": "string"},
            "provider": {"type": "string"},
        },
        "additionalProperties": True,
    },
}


def _tool_schema_for(action: str) -> dict[str, Any]:
    return TOOL_INPUT_SCHEMAS.get(
        action,
        {
            "type": "object",
            "additionalProperties": True,
        },
    )


def _tool_definition(service: OperationsService, action: str) -> dict[str, Any]:
    read_only = action in service.READ_ONLY_ACTIONS
    destructive = action in {
        "invoices.cancel",
        "providers.myinvois.cancel_document",
        "approvals.reject",
    }
    idempotent = read_only or action in {"workflows.status", "approvals.approve", "approvals.reject"}
    return {
        "name": action,
        "title": action.replace(".", " ").title(),
        "description": TOOL_DESCRIPTIONS.get(action, f"Invoke the `{action}` business operation."),
        "inputSchema": _tool_schema_for(action),
        "outputSchema": COMMON_OUTPUT_SCHEMA,
        "annotations": {
            "readOnlyHint": read_only,
            "destructiveHint": destructive,
            "idempotentHint": idempotent,
            "openWorldHint": not read_only,
        },
    }


class McpStdioServer:
    def __init__(self, settings: Settings) -> None:
        self.service = OperationsService(settings)
        self._tool_definitions = [
            _tool_definition(self.service, action)
            for action in sorted(self.service.ACTIONS.keys())
        ]

    def serve_forever(self, in_stream: TextIO | None = None, out_stream: TextIO | None = None) -> None:
        reader = in_stream or sys.stdin
        writer = out_stream or sys.stdout
        for raw_line in reader:
            line = raw_line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                self._write(
                    writer,
                    self._error_response(None, -32700, "Parse error", {"line": line}),
                )
                continue
            response = self._handle_message(message)
            if response is not None:
                self._write(writer, response)

    def _handle_message(self, message: dict[str, Any]) -> dict[str, Any] | None:
        method = message.get("method")
        message_id = message.get("id")
        params = message.get("params") or {}
        if method == "notifications/initialized":
            return None
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    "instructions": "Malaysia-first agent operations tools for autonomous business workflows, approvals, payments, and compliance.",
                },
            }
        if method == "ping":
            return {"jsonrpc": "2.0", "id": message_id, "result": {}}
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {"tools": self._tool_definitions},
            }
        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments") or {}
            if name not in self.service.ACTIONS:
                return self._error_response(message_id, -32602, f"Unknown tool: {name}")
            if not isinstance(arguments, dict):
                return self._error_response(message_id, -32602, "Tool arguments must be an object.")
            try:
                result = self.service.invoke(name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, ensure_ascii=True),
                            }
                        ],
                        "structuredContent": result,
                        "isError": False,
                    },
                }
            except (InputError, NotFoundError) as exc:
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "content": [{"type": "text", "text": str(exc)}],
                        "isError": True,
                    },
                }
        return self._error_response(message_id, -32601, f"Method not found: {method}")

    @staticmethod
    def _error_response(message_id: Any, code: int, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        response: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": message_id,
            "error": {
                "code": code,
                "message": message,
            },
        }
        if data is not None:
            response["error"]["data"] = data
        return response

    @staticmethod
    def _write(writer: TextIO, payload: dict[str, Any]) -> None:
        writer.write(json.dumps(payload, ensure_ascii=True) + "\n")
        writer.flush()


def serve_mcp(settings: Settings) -> None:
    McpStdioServer(settings).serve_forever()
