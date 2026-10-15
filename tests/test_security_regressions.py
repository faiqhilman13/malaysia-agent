"""One test per bypass found in the v0 audit, plus tenant isolation and mandate checks."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from malaysia_agent_ops.db import Approval, Credential
from malaysia_agent_ops.errors import Conflict, Forbidden, NotFound
from malaysia_agent_ops.security.auth import authenticate_api_key
from malaysia_agent_ops.services import admin
from malaysia_agent_ops.services.approvals import ApprovalService

from .conftest import SUPPLIER_TIN, make_invoice
from .test_einvoice_flow import decide, draft_and_approve


def test_v0_bypass_1_agent_cannot_approve_its_own_request(service, rt, notifier, account):
    drafted = service.draft(account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice())
    waiting = service.submit(account.agent, document_id=drafted["resource_id"])
    approval_id = waiting["data"]["approval"]["approval_id"]
    approvals = ApprovalService(notifier=notifier, public_base_url="x")
    with rt.db.session() as s, pytest.raises(Forbidden):
        approvals.decide_as_principal(
            s, account.agent, approval_id=approval_id, approve=True, note=None, now=rt.clock()
        )
    # The agent never sees a decision token: it is not in any response.
    assert all(m.link.split("t=")[1] not in str(waiting) for m in notifier.sent)


def test_requester_cannot_decide_even_with_approver_role(service, rt, notifier, account):
    # An admin key calling tools is still the requester and cannot approve its own request.
    with rt.db.session() as s:
        admin_principal = authenticate_api_key(s, account.admin_key)
    drafted = service.draft(admin_principal, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice())
    waiting = service.submit(admin_principal, document_id=drafted["resource_id"])
    with rt.db.session() as s, pytest.raises(Forbidden):
        ApprovalService(notifier=notifier, public_base_url="x").decide_as_principal(
            s,
            admin_principal,
            approval_id=waiting["data"]["approval"]["approval_id"],
            approve=True,
            note=None,
            now=rt.clock(),
        )


def test_approver_role_cannot_call_agent_tools(service, account):
    result = service.draft(account.approver, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice())
    assert result["status"] == "blocked"


def test_v0_bypass_2_approval_is_bound_to_the_exact_payload(service, rt, notifier, account, fake):
    doc_id = draft_and_approve(service, rt, notifier, account, "INV-A")
    # Change the document after approval: same id, different payload.
    changed = make_invoice("INV-A")
    changed.lines[0].quantity = Decimal("1000")
    service.draft(account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=changed)
    result = service.submit(account.agent, document_id=doc_id)
    assert result["status"] == "awaiting_human_approval"
    assert not fake.submissions


def test_v0_bypass_2b_one_approval_cannot_cover_another_document(service, rt, notifier, account, fake):
    draft_and_approve(service, rt, notifier, account, "INV-A")
    other = service.draft(
        account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice("INV-B")
    )
    assert service.submit(account.agent, document_id=other["resource_id"])["status"] == "awaiting_human_approval"
    assert not fake.submissions


def test_approval_is_single_use(service, rt, notifier, account):
    doc_id = draft_and_approve(service, rt, notifier, account, "INV-S")
    assert service.submit(account.agent, document_id=doc_id)["status"] == "awaiting_external_event"
    with rt.db.session() as s:
        approval = s.scalar(select(Approval).where(Approval.resource_id == doc_id))
        assert approval.status == "consumed"
        with pytest.raises(Conflict):
            ApprovalService(notifier=notifier, public_base_url="x")._decide(
                s, approval, decided_by="user:x", approve=True, note=None, now=rt.clock()
            )


def test_approval_expires(service, rt, notifier, account, clock):
    drafted = service.draft(account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice())
    waiting = service.submit(account.agent, document_id=drafted["resource_id"])
    clock.advance(hours=25)
    with pytest.raises(Conflict):
        decide(rt, notifier, waiting["data"]["approval"]["approval_id"])
    status = service.approval_status(account.agent, approval_id=waiting["data"]["approval"]["approval_id"])
    assert status["data"]["status"] == "expired"


def test_approval_link_is_single_use_and_token_checked(service, rt, notifier, account):
    drafted = service.draft(account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice())
    approval_id = service.submit(account.agent, document_id=drafted["resource_id"])["data"]["approval"]["approval_id"]
    approvals = ApprovalService(notifier=notifier, public_base_url="x")
    with rt.db.session() as s, pytest.raises(NotFound):
        approvals.decide_with_link(
            s,
            approval_id=approval_id,
            user_id=account.approver_user_id,
            token="guess",
            approve=True,
            note=None,
            now=rt.clock(),
        )
    decide(rt, notifier, approval_id)
    with pytest.raises(NotFound):
        decide(rt, notifier, approval_id)


def test_rejected_approval_blocks(service, rt, notifier, account, fake):
    drafted = service.draft(account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice())
    waiting = service.submit(account.agent, document_id=drafted["resource_id"])
    decide(rt, notifier, waiting["data"]["approval"]["approval_id"], approve=False)
    assert service.submit(account.agent, document_id=drafted["resource_id"])["status"] == "blocked"
    assert not fake.submissions


def test_v0_bypass_3_there_is_no_unapproved_low_level_submit(service):
    # v0 let `provider: "sandbox"` on a low-level tool submit for real without approval. The service now
    # exposes exactly one submit path, and it always goes through the approval gate.
    public = {name for name in dir(service) if not name.startswith("_") and callable(getattr(service, name))}
    assert {n for n in public if "submit" in n} == {"submit"}


def test_v0_bypass_4_cancel_in_production_always_needs_approval(service, rt, notifier, account, fake):
    with rt.db.session() as s:
        admin.set_approval_policy(s, account.tenant_id, {"submit": False, "cancel": False})
    drafted = service.draft(account.agent, taxpayer_tin=SUPPLIER_TIN, environment="production", invoice=make_invoice())
    assert service.submit(account.agent, document_id=drafted["resource_id"])["status"] == "awaiting_external_event"
    service.refresh_status(account.agent, document_id=drafted["resource_id"])
    result = service.cancel(account.agent, document_id=drafted["resource_id"], reason="test")
    assert result["status"] == "awaiting_human_approval"


def test_auto_approve_threshold(service, rt, account):
    with rt.db.session() as s:
        admin.set_approval_policy(s, account.tenant_id, {"auto_approve_submit_max": 500})
    small = service.draft(
        account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice("SMALL")
    )
    assert service.submit(account.agent, document_id=small["resource_id"])["status"] == "awaiting_external_event"
    big_invoice = make_invoice("BIG")
    big_invoice.lines[0].quantity = Decimal("100")
    big = service.draft(account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=big_invoice)
    assert service.submit(account.agent, document_id=big["resource_id"])["status"] == "awaiting_human_approval"


def test_tenant_isolation(service, rt, notifier, account):
    drafted = service.draft(account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice())
    with rt.db.session() as s:
        other = admin.create_tenant(s, "Other Firm")
        _, other_key = admin.create_api_key(s, other.id, role="agent", name="other")
    with rt.db.session() as s:
        intruder = authenticate_api_key(s, other_key)
    assert service.get_document(intruder, document_id=drafted["resource_id"])["data"]["error_code"] == "not_found"
    assert service.submit(intruder, document_id=drafted["resource_id"])["data"]["error_code"] == "not_found"
    blocked = service.draft(intruder, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice("X"))
    assert blocked["status"] == "blocked"
    assert service.list_documents(intruder)["data"]["documents"] == []


def test_mandate_permission_and_expiry_are_enforced(service, rt, account, clock):
    with rt.db.session() as s:
        admin.add_taxpayer(
            s, account.tenant_id, tin="C66666666660", id_type="BRN", id_value="201701234567", name="View Only"
        )
        admin.add_appointment(
            s,
            account.tenant_id,
            taxpayer_tin="C66666666660",
            mode="intermediary",
            permissions=["view_documents"],
            valid_from=clock() - timedelta(days=1),
            valid_to=clock() + timedelta(days=2),
        )
    invoice = make_invoice("V-1")
    invoice.supplier.tin = "C66666666660"
    no_perm = service.draft(account.agent, taxpayer_tin="C66666666660", environment="preprod", invoice=invoice)
    assert no_perm["status"] == "blocked" and "submit_documents" in no_perm["blocking_reason"]
    clock.advance(days=400)
    expired = service.draft(
        account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice("E-1")
    )
    assert expired["status"] == "blocked" and "expired" in expired["blocking_reason"]


def test_supplier_must_be_the_mandated_taxpayer(service, account):
    invoice = make_invoice()
    invoice.supplier.tin = "C99999999990"
    result = service.draft(account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=invoice)
    assert result["status"] == "invalid"


def test_secrets_are_encrypted_at_rest_and_never_returned(service, rt, notifier, account):
    with rt.db.session() as s:
        for credential in s.scalars(select(Credential)):
            assert "secret-1" not in credential.ciphertext
    doc_id = draft_and_approve(service, rt, notifier, account)
    outputs = [
        service.submit(account.agent, document_id=doc_id),
        service.refresh_status(account.agent, document_id=doc_id),
        service.list_taxpayers(account.agent),
        service.audit_export(account.agent),
    ]
    for output in outputs:
        text = str(output)
        assert "secret-1" not in text
        assert "tok-" not in text


def test_missing_credentials_block_honestly(service, rt, notifier, account):
    with rt.db.session() as s:
        for credential in s.scalars(select(Credential)):
            s.delete(credential)
    doc_id = draft_and_approve(service, rt, notifier, account)
    result = service.submit(account.agent, document_id=doc_id)
    assert result["status"] == "blocked"
    assert result["data"]["error_code"] == "not_configured"


def test_idempotent_submit_replays_without_resubmitting(service, rt, notifier, account, fake):
    doc_id = draft_and_approve(service, rt, notifier, account)
    first = service.submit(account.agent, document_id=doc_id, idempotency_key="k-1")
    second = service.submit(account.agent, document_id=doc_id, idempotency_key="k-1")
    assert first["status"] == "awaiting_external_event"
    assert second.get("idempotent_replay") is True
    assert len(fake.submissions) == 1
    conflict = service.submit(account.agent, document_id="other", idempotency_key="k-1")
    assert conflict["data"]["error_code"] == "conflict"
