from __future__ import annotations

from decimal import Decimal
from urllib.parse import parse_qs, urlparse

from malaysia_agent_ops.runtime import Runtime
from malaysia_agent_ops.services import admin
from malaysia_agent_ops.services.approvals import ApprovalService
from malaysia_agent_ops.services.einvoice import EInvoiceService
from malaysia_agent_ops.services.notify import MemoryNotifier

from .conftest import BUYER_TIN, EXPECTED_PAYABLE, SUPPLIER_TIN, Account, Clock, make_invoice
from .fake_myinvois import FakeMyInvois


def decide(rt: Runtime, notifier: MemoryNotifier, approval_id: str, approve: bool = True) -> None:
    message = next(m for m in reversed(notifier.sent) if f"/approve/{approval_id}?" in m.link)
    query = parse_qs(urlparse(message.link).query)
    with rt.db.session() as s:
        ApprovalService(notifier=notifier, public_base_url="x").decide_with_link(
            s,
            approval_id=approval_id,
            user_id=query["u"][0],
            token=query["t"][0],
            approve=approve,
            note=None,
            now=rt.clock(),
        )


def draft_and_approve(
    service: EInvoiceService,
    rt: Runtime,
    notifier: MemoryNotifier,
    account: Account,
    code: str = "INV-1001",
    env: str = "preprod",
) -> str:
    drafted = service.draft(account.agent, taxpayer_tin=SUPPLIER_TIN, environment=env, invoice=make_invoice(code))
    assert drafted["status"] == "success", drafted
    doc_id = drafted["resource_id"]
    waiting = service.submit(account.agent, document_id=doc_id)
    assert waiting["status"] == "awaiting_human_approval", waiting
    decide(rt, notifier, waiting["data"]["approval"]["approval_id"])
    return doc_id


def test_full_lifecycle_draft_approve_submit_validate_cancel(service, rt, notifier, account, fake: FakeMyInvois):
    drafted = service.draft(account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice())
    assert drafted["status"] == "success"
    assert drafted["data"]["totals"]["payable"] == str(EXPECTED_PAYABLE)
    assert drafted["data"]["status"] == "draft"
    doc_id = drafted["resource_id"]

    waiting = service.submit(account.agent, document_id=doc_id)
    assert waiting["status"] == "awaiting_human_approval"
    approval_id = waiting["data"]["approval"]["approval_id"]
    assert not fake.submissions, "nothing reaches MyInvois before approval"
    # The approval link goes to the approver, not back to the agent.
    assert {m.email for m in notifier.sent} == {"owner@acme.example", "admin@kira.example"}
    assert "t=" not in str(waiting)

    pending = service.approval_status(account.agent, approval_id=approval_id)
    assert pending["data"]["status"] == "pending"

    decide(rt, notifier, approval_id)
    submitted = service.submit(account.agent, document_id=doc_id)
    assert submitted["status"] == "awaiting_external_event", submitted
    assert submitted["data"]["uuid"]
    assert fake.logins == [SUPPLIER_TIN], "intermediary login carries onbehalfof"

    refreshed = service.refresh_status(account.agent, document_id=doc_id)
    assert refreshed["status"] == "success"
    assert refreshed["data"]["status"] == "valid"
    assert refreshed["data"]["validation_link"].startswith("https://preprod.myinvois.hasil.gov.my/")

    cancel_wait = service.cancel(account.agent, document_id=doc_id, reason="Wrong buyer")
    assert cancel_wait["status"] == "awaiting_human_approval"
    decide(rt, notifier, cancel_wait["data"]["approval"]["approval_id"])
    cancelled = service.cancel(account.agent, document_id=doc_id, reason="Wrong buyer")
    assert cancelled["status"] == "success"
    assert cancelled["data"]["status"] == "cancelled"
    assert fake.documents[submitted["data"]["uuid"]]["status"] == "Cancelled"

    trail = service.audit_export(account.agent)
    assert trail["data"]["chain"]["valid"] is True
    actions = [e["action"] for e in trail["data"]["events"]]
    for expected in (
        "einvoice.draft",
        "approval.requested",
        "approval.decided",
        "einvoice.submit",
        "einvoice.status",
        "einvoice.cancel",
    ):
        assert expected in actions


def test_token_is_cached_per_taxpayer(service, rt, notifier, account, fake):
    for code in ("INV-1", "INV-2"):
        doc_id = draft_and_approve(service, rt, notifier, account, code)
        assert service.submit(account.agent, document_id=doc_id)["status"] == "awaiting_external_event"
    assert len(fake.logins) == 1


def test_rejected_by_myinvois_reports_errors_and_allows_redraft(service, rt, notifier, account, fake):
    fake.reject_codes.add("INV-BAD")
    doc_id = draft_and_approve(service, rt, notifier, account, "INV-BAD")
    result = service.submit(account.agent, document_id=doc_id)
    assert result["status"] == "invalid"
    assert any("Duplicate" in e for e in result["data"]["errors"])
    redraft = service.draft(
        account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice("INV-BAD")
    )
    assert redraft["status"] == "success"
    assert redraft["resource_id"] == doc_id


def test_async_validation_failure_surfaces_validation_errors(service, rt, notifier, account, fake):
    fake.invalid_codes.add("INV-INV")
    doc_id = draft_and_approve(service, rt, notifier, account, "INV-INV")
    assert service.submit(account.agent, document_id=doc_id)["status"] == "awaiting_external_event"
    result = service.refresh_status(account.agent, document_id=doc_id)
    assert result["status"] == "invalid"
    assert any("Buyer TIN not found" in e for e in result["data"]["errors"])


def test_pending_validation_waits(service, rt, notifier, account, fake):
    fake.pending_codes.add("INV-P")
    doc_id = draft_and_approve(service, rt, notifier, account, "INV-P")
    service.submit(account.agent, document_id=doc_id)
    assert service.refresh_status(account.agent, document_id=doc_id)["status"] == "awaiting_external_event"


def test_cannot_redraft_a_submitted_invoice_number(service, rt, notifier, account):
    doc_id = draft_and_approve(service, rt, notifier, account, "INV-9")
    service.submit(account.agent, document_id=doc_id)
    again = service.draft(
        account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice("INV-9")
    )
    assert again["status"] == "error"
    assert again["data"]["error_code"] == "conflict"


def test_issue_time_older_than_72_hours_blocks_submission(service, rt, notifier, account, clock: Clock):
    doc_id = draft_and_approve(service, rt, notifier, account, "INV-OLD")
    clock.advance(hours=73)
    result = service.submit(account.agent, document_id=doc_id)
    assert result["status"] == "blocked"


def test_cancel_after_72_hours_points_to_credit_note(service, rt, notifier, account, clock):
    doc_id = draft_and_approve(service, rt, notifier, account, "INV-LATE")
    service.submit(account.agent, document_id=doc_id)
    service.refresh_status(account.agent, document_id=doc_id)
    clock.advance(hours=73)
    result = service.cancel(account.agent, document_id=doc_id, reason="late")
    assert result["status"] == "blocked"
    assert "credit note" in result["next_action"]


def test_validate_counterparty(service, account):
    ok = service.validate_counterparty(
        account.agent,
        taxpayer_tin=SUPPLIER_TIN,
        environment="preprod",
        tin=BUYER_TIN,
        id_type="BRN",
        id_value="202001234567",
    )
    assert ok["status"] == "success" and ok["data"]["valid"] is True
    bad = service.validate_counterparty(
        account.agent,
        taxpayer_tin=SUPPLIER_TIN,
        environment="preprod",
        tin=BUYER_TIN,
        id_type="BRN",
        id_value="999999999999",
    )
    assert bad["data"]["valid"] is False
    malformed = service.validate_counterparty(
        account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", tin="123", id_type="BRN", id_value="1"
    )
    assert malformed["status"] == "invalid"
    found = service.search_counterparty_tin(
        account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", id_type="BRN", id_value="202001234567"
    )
    assert found["data"]["tin"] == BUYER_TIN


def test_reject_received_document_requires_approval(service, rt, notifier, account, fake, clock):
    fake.received["UUID-IN-1"] = {
        "uuid": "UUID-IN-1",
        "receiverId": SUPPLIER_TIN,
        "internalId": "SUP-77",
        "supplierName": "Vendor Sdn Bhd",
        "supplierTin": "C11111111110",
        "totalPayableAmount": 1200,
        "dateTimeValidated": clock().isoformat(),
        "status": "Valid",
    }
    waiting = service.reject_received(
        account.agent,
        taxpayer_tin=SUPPLIER_TIN,
        environment="production",
        document_uuid="UUID-IN-1",
        reason="Goods not received",
    )
    assert waiting["status"] == "awaiting_human_approval"
    decide(rt, notifier, waiting["data"]["approval"]["approval_id"])
    done = service.reject_received(
        account.agent,
        taxpayer_tin=SUPPLIER_TIN,
        environment="production",
        document_uuid="UUID-IN-1",
        reason="Goods not received",
    )
    assert done["status"] == "success"
    assert fake.received["UUID-IN-1"]["status"] == "Rejected"


def test_consolidated_draft_carves_out_large_receipts(service, account):
    from datetime import date

    from malaysia_agent_ops.myinvois.consolidation import Receipt

    supplier = make_invoice().supplier
    receipts = [
        Receipt(reference="R-001", issued_on=date(2026, 10, 1), amount=Decimal("120")),
        Receipt(
            reference="R-002",
            issued_on=date(2026, 10, 2),
            amount=Decimal("80"),
            tax_type="02",
            tax_amount=Decimal("6.40"),
        ),
        Receipt(reference="R-003", issued_on=date(2026, 10, 3), amount=Decimal("15000")),
    ]
    result = service.draft_consolidated(
        account.agent,
        taxpayer_tin=SUPPLIER_TIN,
        environment="preprod",
        month="2026-10",
        supplier=supplier,
        receipts=receipts,
        code_number="CONS-2026-10",
    )
    assert result["status"] == "success", result
    data = result["data"]
    assert data["buyer"]["tin"] == "EI00000000010"
    assert data["totals"]["payable"] == "206.40"
    assert [r["reference"] for r in data["individual_einvoice_required"]] == ["R-003"]
    assert data["submit_by"] == "2026-11-07"


def test_self_mode_uses_taxpayer_credentials_without_onbehalfof(rt, service, notifier, account, fake, clock):
    from datetime import timedelta

    with rt.db.session() as s:
        admin.add_taxpayer(
            s, account.tenant_id, tin="C77777777770", id_type="BRN", id_value="201801234567", name="Self Co"
        )
        admin.add_appointment(
            s,
            account.tenant_id,
            taxpayer_tin="C77777777770",
            mode="self",
            permissions=["view_documents", "submit_documents"],
            valid_from=clock() - timedelta(days=1),
            valid_to=clock() + timedelta(days=30),
        )
        admin.store_credential(
            s,
            rt.vault,
            account.tenant_id,
            kind="myinvois_client",
            environment="preprod",
            secret={"client_id": "client-1", "client_secret": "secret-1"},
            taxpayer_tin="C77777777770",
        )
    invoice = make_invoice("SELF-1")
    invoice.supplier.tin = "C77777777770"
    drafted = service.draft(account.agent, taxpayer_tin="C77777777770", environment="preprod", invoice=invoice)
    decide(
        rt,
        notifier,
        service.submit(account.agent, document_id=drafted["resource_id"])["data"]["approval"]["approval_id"],
    )
    assert service.submit(account.agent, document_id=drafted["resource_id"])["status"] == "awaiting_external_event"
    assert fake.logins == [None]
