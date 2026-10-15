from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from malaysia_agent_ops.api.app import create_app

from .conftest import SUPPLIER_TIN, invoice_payload


def _auth(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}"}


def test_rest_requires_auth(rt, account):
    with TestClient(create_app(rt)) as client:
        response = client.get("/v1/taxpayers")
        assert response.status_code == 401
        assert response.json()["data"]["error_code"] == "unauthenticated"
        assert client.get("/health").status_code == 200


def test_rest_flow_with_approval_page(rt, account, notifier, fake):
    with TestClient(create_app(rt)) as client:
        draft = client.post(
            "/v1/einvoices/drafts",
            json={"taxpayer_tin": SUPPLIER_TIN, "environment": "preprod", "invoice": invoice_payload("REST-1")},
            headers=_auth(account.agent_key),
        )
        assert draft.status_code == 200, draft.text
        doc_id = draft.json()["resource_id"]

        waiting = client.post(
            f"/v1/einvoices/{doc_id}/submit", headers={**_auth(account.agent_key), "Idempotency-Key": "r1"}
        )
        assert waiting.status_code == 202
        assert waiting.json()["status"] == "awaiting_human_approval"
        approval_id = waiting.json()["data"]["approval"]["approval_id"]

        # The agent key cannot use the decision endpoint.
        refused = client.post(
            f"/v1/approvals/{approval_id}/decision", json={"approve": True}, headers=_auth(account.agent_key)
        )
        assert refused.status_code == 403

        # The human opens the link from their WhatsApp/email. GET only shows the page.
        link = next(m.link for m in notifier.sent if m.email == "owner@acme.example")
        parsed = urlparse(link)
        page = client.get(f"{parsed.path}?{parsed.query}")
        assert page.status_code == 200
        assert "REST-1" in page.text and "MYR 439.00" in page.text
        assert page.headers["referrer-policy"] == "no-referrer"
        query = parse_qs(parsed.query)
        decided = client.post(parsed.path, data={"u": query["u"][0], "t": query["t"][0], "decision": "approve"})
        assert decided.status_code == 200 and "approved" in decided.text
        reused = client.post(parsed.path, data={"u": query["u"][0], "t": query["t"][0], "decision": "approve"})
        assert reused.status_code == 409

        submitted = client.post(
            f"/v1/einvoices/{doc_id}/submit", headers={**_auth(account.agent_key), "Idempotency-Key": "r1"}
        )
        assert submitted.status_code == 202
        assert submitted.json()["status"] == "awaiting_external_event"

        status = client.post(f"/v1/einvoices/{doc_id}/refresh-status", headers=_auth(account.agent_key))
        assert status.json()["data"]["status"] == "valid"
        listed = client.get("/v1/einvoices", headers=_auth(account.agent_key))
        assert listed.json()["data"]["documents"][0]["code_number"] == "REST-1"
        trail = client.get("/v1/audit", headers=_auth(account.agent_key))
        assert trail.json()["data"]["chain"]["valid"] is True


def test_approver_key_can_decide_via_api(rt, account):
    with TestClient(create_app(rt)) as client:
        draft = client.post(
            "/v1/einvoices/drafts",
            json={"taxpayer_tin": SUPPLIER_TIN, "invoice": invoice_payload("REST-2")},
            headers=_auth(account.agent_key),
        )
        approval_id = client.post(
            f"/v1/einvoices/{draft.json()['resource_id']}/submit", headers=_auth(account.agent_key)
        ).json()["data"]["approval"]["approval_id"]
        decided = client.post(
            f"/v1/approvals/{approval_id}/decision",
            json={"approve": False, "note": "wrong amount"},
            headers=_auth(account.approver_key),
        )
        assert decided.status_code == 200
        assert decided.json()["data"]["status"] == "rejected"


def test_invalid_body_returns_envelope(rt, account):
    bad = invoice_payload("REST-3")
    bad["lines"][0]["classification_code"] = "999"
    with TestClient(create_app(rt)) as client:
        response = client.post(
            "/v1/einvoices/drafts",
            json={"taxpayer_tin": SUPPLIER_TIN, "invoice": bad},
            headers=_auth(account.agent_key),
        )
        assert response.status_code == 422
        body = response.json()
        assert body["status"] == "invalid"
        assert any(re.search("classification_code", issue["field"]) for issue in body["data"]["issues"])


def test_bad_approval_link(rt, account):
    with TestClient(create_app(rt)) as client:
        assert client.get("/approve/nope?u=x&t=y").status_code == 404
