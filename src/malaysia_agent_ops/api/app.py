"""HTTP service: REST API for software vendors, the approval page for humans, and remote MCP at /mcp."""

from __future__ import annotations

import html
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any

import anyio
from fastapi import Depends, FastAPI, Form, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from .. import __version__
from ..envelope import envelope, error_envelope
from ..errors import OpsError, Unauthenticated
from ..myinvois.consolidation import Receipt
from ..myinvois.invoice import InvoiceInput, Party
from ..runtime import Runtime
from ..security.auth import Principal, authenticate_bearer
from ..services.approvals import ApprovalService, public_view
from ..services.einvoice import EInvoiceService
from .mcp_server import build_mcp, transport_security

_STATUS_CODES = {
    "success": 200,
    "awaiting_human_approval": 202,
    "awaiting_external_event": 202,
    "invalid": 422,
}
_ERROR_CODES = {
    "not_found": 404,
    "conflict": 409,
    "forbidden": 403,
    "unauthenticated": 401,
    "not_configured": 412,
    "rate_limited": 429,
    "upstream_error": 502,
}


def respond(result: dict[str, Any]) -> JSONResponse:
    code = _STATUS_CODES.get(result["status"])
    if code is None:
        code = _ERROR_CODES.get(result.get("data", {}).get("error_code"), 409 if result["status"] == "blocked" else 400)
    return JSONResponse(result, status_code=code)


class DraftRequest(BaseModel):
    taxpayer_tin: str
    environment: str = "preprod"
    invoice: InvoiceInput


class ConsolidatedRequest(BaseModel):
    taxpayer_tin: str
    environment: str = "preprod"
    month: str = Field(description="YYYY-MM")
    supplier: Party
    receipts: list[Receipt]
    code_number: str


class ValidateTinRequest(BaseModel):
    taxpayer_tin: str
    environment: str = "preprod"
    tin: str
    id_type: str
    id_value: str


class ReasonRequest(BaseModel):
    reason: str


class RejectRequest(BaseModel):
    taxpayer_tin: str
    environment: str = "preprod"
    reason: str


class DecisionRequest(BaseModel):
    approve: bool
    note: str | None = None


async def _principal(request: Request, authorization: Annotated[str | None, Header()] = None) -> Principal:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise Unauthenticated("Send Authorization: Bearer <api key or access token>.")
    rt: Runtime = request.app.state.rt

    def authenticate() -> Principal:
        with rt.db.session() as s:
            return authenticate_bearer(s, authorization[7:].strip(), rt.jwt)

    return await anyio.to_thread.run_sync(authenticate)


Caller = Annotated[Principal, Depends(_principal)]


def create_app(rt: Runtime | None = None) -> FastAPI:
    rt = rt or Runtime.from_settings()
    service = EInvoiceService(rt)
    approvals = ApprovalService(notifier=rt.notifier, public_base_url=rt.settings.public_base_url)
    mcp = build_mcp(rt, service)
    mcp_app = mcp.streamable_http_app(
        streamable_http_path="/mcp", stateless_http=True, json_response=True, transport_security=transport_security(rt)
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        async with mcp.session_manager.run():
            yield

    app = FastAPI(
        title="Malaysia Agent Ops",
        version=__version__,
        description="Compliance-grade MyInvois e-invoicing for AI agents. The same core serves REST and MCP (/mcp).",
        lifespan=lifespan,
    )

    @app.exception_handler(OpsError)
    async def _ops_error(_request: Request, exc: OpsError) -> JSONResponse:
        return respond(error_envelope(exc))

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
        issues = [
            {"field": ".".join(str(p) for p in e.get("loc", ()) if p != "body"), "problem": e.get("msg")}
            for e in exc.errors()
        ]
        return respond(
            envelope(
                "invalid",
                data={"issues": issues},
                blocking_reason="The request has invalid fields.",
                next_action="Fix the fields listed in data.issues and retry.",
            )
        )

    app.state.rt = rt

    async def run(fn: Any, *args: Any, **kwargs: Any) -> JSONResponse:
        return respond(await anyio.to_thread.run_sync(lambda: fn(*args, **kwargs)))

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/v1/taxpayers")
    async def list_taxpayers(who: Caller) -> JSONResponse:
        return await run(service.list_taxpayers, who)

    @app.post("/v1/counterparties/validate")
    async def validate_tin(body: ValidateTinRequest, who: Caller) -> JSONResponse:
        return await run(service.validate_counterparty, who, **body.model_dump())

    @app.post("/v1/einvoices/drafts")
    async def draft(body: DraftRequest, who: Caller) -> JSONResponse:
        return await run(
            service.draft, who, taxpayer_tin=body.taxpayer_tin, environment=body.environment, invoice=body.invoice
        )

    @app.post("/v1/einvoices/consolidated-drafts")
    async def draft_consolidated(body: ConsolidatedRequest, who: Caller) -> JSONResponse:
        return await run(
            service.draft_consolidated,
            who,
            taxpayer_tin=body.taxpayer_tin,
            environment=body.environment,
            month=body.month,
            supplier=body.supplier,
            receipts=body.receipts,
            code_number=body.code_number,
        )

    @app.get("/v1/einvoices")
    async def list_documents(
        who: Caller, taxpayer_tin: str | None = None, status: str | None = None, limit: int = 50
    ) -> JSONResponse:
        return await run(service.list_documents, who, taxpayer_tin=taxpayer_tin, status=status, limit=limit)

    @app.get("/v1/einvoices/{document_id}")
    async def get_document(document_id: str, who: Caller) -> JSONResponse:
        return await run(service.get_document, who, document_id=document_id)

    @app.post("/v1/einvoices/{document_id}/submit")
    async def submit(
        document_id: str, who: Caller, idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None
    ) -> JSONResponse:
        return await run(service.submit, who, document_id=document_id, idempotency_key=idempotency_key)

    @app.post("/v1/einvoices/{document_id}/refresh-status")
    async def refresh(document_id: str, who: Caller) -> JSONResponse:
        return await run(service.refresh_status, who, document_id=document_id)

    @app.post("/v1/einvoices/{document_id}/cancel")
    async def cancel(
        document_id: str,
        body: ReasonRequest,
        who: Caller,
        idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    ) -> JSONResponse:
        return await run(
            service.cancel, who, document_id=document_id, reason=body.reason, idempotency_key=idempotency_key
        )

    @app.post("/v1/received/{document_uuid}/reject")
    async def reject(
        document_uuid: str,
        body: RejectRequest,
        who: Caller,
        idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    ) -> JSONResponse:
        return await run(
            service.reject_received,
            who,
            taxpayer_tin=body.taxpayer_tin,
            environment=body.environment,
            document_uuid=document_uuid,
            reason=body.reason,
            idempotency_key=idempotency_key,
        )

    @app.get("/v1/approvals/{approval_id}")
    async def approval_status(approval_id: str, who: Caller) -> JSONResponse:
        return await run(service.approval_status, who, approval_id=approval_id)

    @app.post("/v1/approvals/{approval_id}/decision")
    async def decide(approval_id: str, body: DecisionRequest, who: Caller) -> JSONResponse:
        """For approver-role keys bound to a user. Agent keys are refused."""

        def go() -> dict[str, Any]:
            with rt.db.session() as s:
                approval = approvals.decide_as_principal(
                    s, who, approval_id=approval_id, approve=body.approve, note=body.note, now=rt.clock()
                )
                return envelope("success", data=public_view(approval, rt.clock()), resource_id=approval.id)

        return respond(await anyio.to_thread.run_sync(go))

    @app.get("/v1/audit")
    async def audit_export(who: Caller, after_id: int = 0, limit: int = 200) -> JSONResponse:
        return await run(service.audit_export, who, after_id=after_id, limit=limit)

    # -- approval page (humans, via the one-time link) -------------------------------------------

    @app.get("/approve/{approval_id}", response_class=HTMLResponse)
    async def approval_page(approval_id: str, u: str, t: str) -> HTMLResponse:
        # GET only shows the request; link scanners that prefetch URLs cannot approve anything.
        def go() -> str:
            with rt.db.session() as s:
                approval = approvals.get_for_link(s, approval_id, u, t)
                return _approval_page(public_view(approval, rt.clock()), u, t)

        try:
            return _html(await anyio.to_thread.run_sync(go))
        except OpsError as exc:
            return _html(_message_page("Link not valid", exc.message), 404)

    @app.post("/approve/{approval_id}", response_class=HTMLResponse)
    async def approval_decide(
        approval_id: str,
        u: Annotated[str, Form()],
        t: Annotated[str, Form()],
        decision: Annotated[str, Form()],
        note: Annotated[str | None, Form()] = None,
    ) -> HTMLResponse:
        def go() -> str:
            with rt.db.session() as s:
                approval = approvals.decide_with_link(
                    s,
                    approval_id=approval_id,
                    user_id=u,
                    token=t,
                    approve=decision == "approve",
                    note=note,
                    now=rt.clock(),
                )
                word = "approved" if approval.status == "approved" else "rejected"
                return _message_page(f"Request {word}", "The agent can now continue. You can close this page.")

        try:
            return _html(await anyio.to_thread.run_sync(go))
        except OpsError as exc:
            return _html(_message_page("Could not record your decision", exc.message), 409)

    app.mount("/", mcp_app)
    return app


def _html(body: str, status: int = 200) -> HTMLResponse:
    return HTMLResponse(
        body,
        status_code=status,
        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY"},
    )


_STYLE = (
    "body{font-family:system-ui,sans-serif;max-width:560px;margin:40px auto;padding:0 16px;color:#1a1a1a}"
    "table{border-collapse:collapse;width:100%}td{padding:6px 4px;border-bottom:1px solid #ddd;vertical-align:top}"
    "td:first-child{color:#555;width:30%}button{font-size:16px;padding:10px 18px;margin-right:8px;border-radius:6px;"
    "border:1px solid #999;cursor:pointer}.ok{background:#0b6e4f;color:#fff;border-color:#0b6e4f}"
    "textarea{width:100%;min-height:60px;margin:12px 0}"
)


def _approval_page(view: dict[str, Any], user_id: str, token: str) -> str:
    summary = view["summary"]
    rows = "".join(
        f"<tr><td>{html.escape(k.replace('_', ' ').capitalize())}</td><td>{html.escape(str(v))}</td></tr>"
        for k, v in summary.items()
        if k != "title"
    )
    decided = view["status"] != "pending"
    form = (
        f"<p>This request is <b>{html.escape(view['status'])}</b>.</p>"
        if decided
        else (
            f'<form method="post"><input type="hidden" name="u" value="{html.escape(user_id)}">'
            f'<input type="hidden" name="t" value="{html.escape(token)}">'
            '<label>Note (optional)<textarea name="note"></textarea></label>'
            '<button class="ok" name="decision" value="approve">Approve</button>'
            '<button name="decision" value="reject">Reject</button></form>'
        )
    )
    return (
        f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
        f"<title>Approval request</title><style>{_STYLE}</style></head><body>"
        f"<h1>{html.escape(summary.get('title', view['action']))}</h1><table>{rows}"
        f"<tr><td>Expires</td><td>{html.escape(view['expires_at'])}</td></tr></table>{form}</body></html>"
    )


def _message_page(title: str, message: str) -> str:
    return (
        f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
        f"<title>{html.escape(title)}</title><style>{_STYLE}</style></head><body><h1>{html.escape(title)}</h1>"
        f"<p>{html.escape(message)}</p></body></html>"
    )
