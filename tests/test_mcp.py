from __future__ import annotations

import json
import re

import anyio
from fastapi.testclient import TestClient
from mcp import Client

from malaysia_agent_ops.api.app import create_app
from malaysia_agent_ops.api.mcp_server import build_mcp
from malaysia_agent_ops.services.einvoice import EInvoiceService

from .conftest import SUPPLIER_TIN, invoice_payload

EXPECTED_TOOLS = {
    "taxpayers_list",
    "counterparty_validate_tin",
    "counterparty_search_tin",
    "einvoice_draft",
    "einvoice_draft_consolidated",
    "einvoice_submit",
    "einvoice_get",
    "einvoice_list",
    "einvoice_refresh_status",
    "einvoice_cancel",
    "einvoice_reject_received",
    "approval_get_status",
    "audit_export",
}
DESTRUCTIVE = {"einvoice_submit", "einvoice_cancel", "einvoice_reject_received"}
WRITES = DESTRUCTIVE | {"einvoice_draft", "einvoice_draft_consolidated"}


def _list_tools(rt, account):
    mcp = build_mcp(rt, EInvoiceService(rt), fixed_principal=account.agent)

    async def go():
        async with Client(mcp) as client:
            return (await client.list_tools()).tools

    return anyio.run(go)


def test_tool_contract(rt, account):
    tools = {tool.name: tool for tool in _list_tools(rt, account)}
    assert set(tools) == EXPECTED_TOOLS
    for name, tool in tools.items():
        # Function-name rules shared by Anthropic and OpenAI (v0 used dotted names that broke them).
        assert re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", name)
        assert tool.description and tool.annotations and tool.annotations.title
        assert tool.input_schema["type"] == "object"
        hints = tool.annotations
        if name in WRITES:
            assert hints.read_only_hint is False, name
        else:
            assert hints.read_only_hint is True, name
        assert hints.destructive_hint is (name in DESTRUCTIVE), name
        # No tool can decide an approval or take a secret.
        schema = json.dumps(tool.input_schema).lower()
        assert "client_secret" not in schema and "password" not in schema
    assert not any("approve" in name and "status" not in name for name in tools)


def test_draft_through_mcp_in_process(rt, account):
    mcp = build_mcp(rt, EInvoiceService(rt), fixed_principal=account.agent)

    async def go():
        async with Client(mcp) as client:
            return await client.call_tool(
                "einvoice_draft",
                {"taxpayer_tin": SUPPLIER_TIN, "environment": "preprod", "invoice": invoice_payload("MCP-1")},
            )

    result = anyio.run(go)
    assert result.is_error is False
    assert result.structured_content["status"] == "success"
    assert result.structured_content["data"]["code_number"] == "MCP-1"


def test_invalid_tool_input_is_rejected_by_schema(rt, account):
    mcp = build_mcp(rt, EInvoiceService(rt), fixed_principal=account.agent)
    bad = invoice_payload("MCP-2")
    bad["supplier"]["address"]["state_code"] = "99"

    async def go():
        async with Client(mcp) as client:
            return await client.call_tool("einvoice_draft", {"taxpayer_tin": SUPPLIER_TIN, "invoice": bad})

    result = anyio.run(go)
    assert result.is_error is True
    assert "state code" in str(result.content[0])


def _rpc(client: TestClient, key: str | None, method: str, params: dict | None = None, rpc_id: int = 1):
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": "2025-11-25",
    }
    if key:
        headers["Authorization"] = f"Bearer {key}"
    body = {"jsonrpc": "2.0", "id": rpc_id, "method": method}
    if params is not None:
        body["params"] = params
    return client.post("/mcp", json=body, headers=headers)


def test_remote_mcp_requires_auth_and_advertises_metadata(rt, account):
    rt.settings.public_base_url = "http://testserver"
    with TestClient(create_app(rt)) as client:
        denied = _rpc(client, None, "tools/list")
        assert denied.status_code == 401
        assert "resource_metadata=" in denied.headers["www-authenticate"]
        assert _rpc(client, "myops_not-a-real-key", "tools/list").status_code == 401
        metadata = client.get("/.well-known/oauth-protected-resource/mcp").json()
        assert metadata["resource"] == "http://testserver/mcp"


def test_remote_mcp_end_to_end_with_api_key(rt, account):
    rt.settings.public_base_url = "http://testserver"
    with TestClient(create_app(rt)) as client:
        init = _rpc(
            client,
            account.agent_key,
            "initialize",
            {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"},
            },
        )
        assert init.status_code == 200
        call = _rpc(client, account.agent_key, "tools/call", {"name": "taxpayers_list", "arguments": {}}, rpc_id=2)
        result = call.json()["result"]["structuredContent"]
        assert result["status"] == "success"
        assert result["data"]["taxpayers"][0]["tin"] == SUPPLIER_TIN
        # Approver keys are for humans; they cannot drive agent tools.
        as_approver = _rpc(
            client, account.approver_key, "tools/call", {"name": "taxpayers_list", "arguments": {}}, rpc_id=3
        )
        assert as_approver.json()["result"]["structuredContent"]["status"] == "blocked"


def test_untrusted_host_is_refused(rt, account):
    with TestClient(create_app(rt), base_url="http://evil.example") as client:
        response = _rpc(client, account.agent_key, "tools/list")
        assert response.status_code in (400, 421)
