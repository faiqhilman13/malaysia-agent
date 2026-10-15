"""Remote MCP server (Streamable HTTP, official SDK) exposing workflow-level e-invoice tools.

Design rules:
- Tool names use underscores; every tool declares read-only or destructive.
- Read and write tools are separate; there is no catch-all tool.
- No tool accepts or returns secrets, and no tool can decide an approval.
"""

from __future__ import annotations

from dataclasses import asdict
from functools import partial
from typing import Annotated, Any
from urllib.parse import urlparse

import anyio
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import __version__
from ..errors import Unauthenticated
from ..myinvois.consolidation import Receipt
from ..myinvois.invoice import InvoiceInput, Party
from ..runtime import Runtime
from ..security.auth import Principal, authenticate_bearer
from ..services.einvoice import EInvoiceService

INSTRUCTIONS = """\
Issue, track and correct Malaysian e-invoices in LHDN MyInvois for the businesses this account may act for.

Workflow:
1. taxpayers_list to see which businesses you may act for and what you may do.
2. counterparty_validate_tin before invoicing a new buyer.
3. einvoice_draft (or einvoice_draft_consolidated for monthly B2C sales) returns a preview. Show it to the user.
4. einvoice_submit. If the result is awaiting_human_approval, a human approver has been sent a link; poll
   approval_get_status and call einvoice_submit again once approved. You cannot approve on anyone's behalf.
5. einvoice_refresh_status until the document is valid or invalid.
Corrections: einvoice_cancel within 72 hours of validation; after that, draft a credit note (document_type 02).

Every result has status, next_action and blocking_reason. Follow next_action. Never ask the user for MyInvois
client secrets or certificates; an admin stores those outside this conversation.
Use environment "preprod" for testing and "production" only when the user means it.
"""

Env = Annotated[str, Field(description='"preprod" (LHDN sandbox) or "production".')]
TaxpayerTin = Annotated[str, Field(description="TIN of the business you are acting for (from taxpayers_list).")]
DocumentId = Annotated[str, Field(description="document_id returned by einvoice_draft.")]
IdempotencyKey = Annotated[
    str | None, Field(description="Optional. Reuse the same key when retrying so the action happens once.")
]


def _hints(
    *, read_only: bool, destructive: bool = False, idempotent: bool = True, open_world: bool = False, title: str
) -> ToolAnnotations:
    return ToolAnnotations(
        title=title,
        read_only_hint=read_only,
        destructive_hint=destructive,
        idempotent_hint=idempotent,
        open_world_hint=open_world,
    )


class BearerVerifier:
    """MCP TokenVerifier accepting this service's API keys, or JWTs from the configured OAuth server."""

    def __init__(self, rt: Runtime) -> None:
        self.rt = rt
        self.jwt = rt.jwt

    def _verify(self, token: str) -> Principal:
        with self.rt.db.session() as s:
            return authenticate_bearer(s, token, self.jwt)

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            principal = await anyio.to_thread.run_sync(self._verify, token)
        except Unauthenticated:
            return None
        return AccessToken(
            token=token,
            client_id=principal.subject,
            scopes=[principal.role],
            subject=principal.subject,
            claims={"principal": asdict(principal)},
        )


def transport_security(rt: Runtime) -> TransportSecuritySettings:
    public = urlparse(rt.settings.public_base_url)
    hosts = [
        "127.0.0.1",
        "localhost",
        "[::1]",
        "127.0.0.1:*",
        "localhost:*",
        "[::1]:*",
        public.netloc,
        *rt.settings.mcp_allowed_hosts,
    ]
    origins = ["http://127.0.0.1:*", "http://localhost:*", f"{public.scheme}://{public.netloc}"]
    return TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=hosts, allowed_origins=origins)


def build_mcp(rt: Runtime, service: EInvoiceService, *, fixed_principal: Principal | None = None) -> MCPServer:
    """`fixed_principal` is for stdio: the caller authenticated once at startup with an API key."""
    verifier = None if fixed_principal else BearerVerifier(rt)
    auth = None
    if verifier is not None:
        base = rt.settings.public_base_url.rstrip("/")
        auth = AuthSettings(
            issuer_url=rt.settings.oauth_issuer or base,
            resource_server_url=f"{base}/mcp",
            validate_token_resource=False,  # API keys have no audience; JWT audience is checked by JwtVerifier
        )
    mcp = MCPServer(
        name="malaysia-agent-ops",
        title="Malaysia e-Invoicing (MyInvois)",
        description=(
            "Compliance-grade MyInvois e-invoicing for AI agents, under each business's intermediary appointment."
        ),
        instructions=INSTRUCTIONS,
        version=__version__,
        token_verifier=verifier,
        auth=auth,
    )

    def principal() -> Principal:
        if fixed_principal is not None:
            return fixed_principal
        token = get_access_token()
        if token is None or not token.claims or "principal" not in token.claims:
            raise Unauthenticated("Missing bearer token.")
        return Principal(**token.claims["principal"])

    async def call(method: Any, **kwargs: Any) -> dict[str, Any]:
        who = principal()  # read the request context before switching threads
        return await anyio.to_thread.run_sync(partial(method, who, **kwargs))

    @mcp.tool(name="taxpayers_list", annotations=_hints(read_only=True, title="List businesses you can act for"))
    async def taxpayers_list() -> dict[str, Any]:
        """List the businesses this account may act for, the permissions granted, and whether MyInvois
        credentials are set up for preprod and production."""
        return await call(service.list_taxpayers)

    @mcp.tool(
        name="counterparty_validate_tin",
        annotations=_hints(read_only=True, open_world=True, title="Validate a buyer's TIN with LHDN"),
    )
    async def counterparty_validate_tin(
        taxpayer_tin: TaxpayerTin,
        tin: Annotated[str, Field(description="The counterparty's TIN.")],
        id_type: Annotated[str, Field(description="BRN, NRIC, PASSPORT or ARMY.")],
        id_value: Annotated[str, Field(description="The registration or identity number for id_type.")],
        environment: Env = "preprod",
    ) -> dict[str, Any]:
        """Check with MyInvois that a TIN matches the given registration or identity number."""
        return await call(
            service.validate_counterparty,
            taxpayer_tin=taxpayer_tin,
            environment=environment,
            tin=tin,
            id_type=id_type,
            id_value=id_value,
        )

    @mcp.tool(
        name="counterparty_search_tin",
        annotations=_hints(read_only=True, open_world=True, title="Find a TIN by registration number"),
    )
    async def counterparty_search_tin(
        taxpayer_tin: TaxpayerTin,
        id_type: Annotated[str | None, Field(description="BRN, NRIC, PASSPORT or ARMY.")] = None,
        id_value: Annotated[str | None, Field(description="Registration or identity number.")] = None,
        name: Annotated[str | None, Field(description="Registered name, if no number is known.")] = None,
        environment: Env = "preprod",
    ) -> dict[str, Any]:
        """Look up a counterparty's TIN in MyInvois by registration/identity number or name."""
        return await call(
            service.search_counterparty_tin,
            taxpayer_tin=taxpayer_tin,
            environment=environment,
            id_type=id_type,
            id_value=id_value,
            name=name,
        )

    @mcp.tool(name="einvoice_draft", annotations=_hints(read_only=False, title="Draft an e-invoice"))
    async def einvoice_draft(
        taxpayer_tin: TaxpayerTin, invoice: InvoiceInput, environment: Env = "preprod"
    ) -> dict[str, Any]:
        """Validate and total an invoice, credit/debit/refund note or self-billed document and save it as a
        draft. Nothing is sent to MyInvois. Returns a preview to show the user and a document_id. Calling it
        again with the same code_number replaces the draft (and voids any approval for the old version)."""
        return await call(service.draft, taxpayer_tin=taxpayer_tin, environment=environment, invoice=invoice)

    @mcp.tool(
        name="einvoice_draft_consolidated",
        annotations=_hints(read_only=False, title="Draft a monthly consolidated e-invoice"),
    )
    async def einvoice_draft_consolidated(
        taxpayer_tin: TaxpayerTin,
        month: Annotated[str, Field(description="YYYY-MM of the sales being consolidated.")],
        supplier: Party,
        receipts: list[Receipt],
        code_number: Annotated[str, Field(description="Invoice number for the consolidated e-invoice.")],
        environment: Env = "preprod",
    ) -> dict[str, Any]:
        """Build a consolidated B2C e-invoice for a month of receipts. Receipts above RM10,000 are left out
        and listed in individual_einvoice_required, because each needs its own e-invoice. Also returns the
        submit-by date (7 days after month end)."""
        return await call(
            service.draft_consolidated,
            taxpayer_tin=taxpayer_tin,
            environment=environment,
            month=month,
            supplier=supplier,
            receipts=receipts,
            code_number=code_number,
        )

    @mcp.tool(
        name="einvoice_submit",
        annotations=_hints(read_only=False, destructive=True, open_world=True, title="Submit an e-invoice to MyInvois"),
    )
    async def einvoice_submit(document_id: DocumentId, idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
        """Submit a drafted document to MyInvois. This is legally binding in production. If a human approval
        is required, the first call returns awaiting_human_approval and sends the approver a link; call
        again after approval_get_status shows approved."""
        return await call(service.submit, document_id=document_id, idempotency_key=idempotency_key)

    @mcp.tool(name="einvoice_get", annotations=_hints(read_only=True, title="Get an e-invoice"))
    async def einvoice_get(document_id: DocumentId) -> dict[str, Any]:
        """Return a document's current state as last recorded (no MyInvois call)."""
        return await call(service.get_document, document_id=document_id)

    @mcp.tool(name="einvoice_list", annotations=_hints(read_only=True, title="List e-invoices"))
    async def einvoice_list(
        taxpayer_tin: Annotated[str | None, Field(description="Only this business.")] = None,
        status: Annotated[str | None, Field(description="draft, submitted, valid, invalid or cancelled.")] = None,
        limit: Annotated[int, Field(ge=1, le=200)] = 50,
    ) -> dict[str, Any]:
        """List recent documents, newest first."""
        return await call(service.list_documents, taxpayer_tin=taxpayer_tin, status=status, limit=limit)

    @mcp.tool(
        name="einvoice_refresh_status",
        annotations=_hints(read_only=True, open_world=True, title="Check validation status with MyInvois"),
    )
    async def einvoice_refresh_status(document_id: DocumentId) -> dict[str, Any]:
        """Ask MyInvois for the latest status of a submitted document. Returns the validation link when
        valid, or the validation errors when invalid. Changes nothing in MyInvois."""
        return await call(service.refresh_status, document_id=document_id)

    @mcp.tool(
        name="einvoice_cancel",
        annotations=_hints(read_only=False, destructive=True, open_world=True, title="Cancel a validated e-invoice"),
    )
    async def einvoice_cancel(
        document_id: DocumentId,
        reason: Annotated[str, Field(description="Why it is being cancelled (max 300 characters).")],
        idempotency_key: IdempotencyKey = None,
    ) -> dict[str, Any]:
        """Cancel a validated document within 72 hours of validation. Needs human approval. After 72 hours,
        draft a credit note instead (the result says how)."""
        return await call(service.cancel, document_id=document_id, reason=reason, idempotency_key=idempotency_key)

    @mcp.tool(
        name="einvoice_reject_received",
        annotations=_hints(
            read_only=False, destructive=True, open_world=True, title="Reject an e-invoice you received"
        ),
    )
    async def einvoice_reject_received(
        taxpayer_tin: TaxpayerTin,
        document_uuid: Annotated[str, Field(description="MyInvois UUID of the received document.")],
        reason: Annotated[str, Field(description="Why it is being rejected (max 300 characters).")],
        environment: Env = "preprod",
        idempotency_key: IdempotencyKey = None,
    ) -> dict[str, Any]:
        """As the buyer, request rejection of an e-invoice issued to this business, within 72 hours of
        validation. Needs human approval."""
        return await call(
            service.reject_received,
            taxpayer_tin=taxpayer_tin,
            environment=environment,
            document_uuid=document_uuid,
            reason=reason,
            idempotency_key=idempotency_key,
        )

    @mcp.tool(name="approval_get_status", annotations=_hints(read_only=True, title="Check an approval"))
    async def approval_get_status(
        approval_id: Annotated[str, Field(description="approval_id from an earlier result.")],
    ) -> dict[str, Any]:
        """See whether a human has approved, rejected, or not yet decided. Approvals cannot be granted here."""
        return await call(service.approval_status, approval_id=approval_id)

    @mcp.tool(name="audit_export", annotations=_hints(read_only=True, title="Export the audit trail"))
    async def audit_export(
        after_id: Annotated[int, Field(ge=0, description="Return events after this id (for paging).")] = 0,
        limit: Annotated[int, Field(ge=1, le=1000)] = 200,
    ) -> dict[str, Any]:
        """Return audit events and whether the tamper-evident hash chain verifies."""
        return await call(service.audit_export, after_id=after_id, limit=limit)

    return mcp
