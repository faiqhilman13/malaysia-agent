"""Unit tests for the MyInvois engine: invoice model, UBL, signing, client behaviour, audit and vault."""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import httpx
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from pydantic import ValidationError
from sqlalchemy import text

from malaysia_agent_ops.errors import NotConfigured, RateLimited
from malaysia_agent_ops.myinvois import consolidation
from malaysia_agent_ops.myinvois.client import ClientCredentials, MyInvoisClient, RateLimiter, TokenCache
from malaysia_agent_ops.myinvois.invoice import InvoiceInput, compute_totals
from malaysia_agent_ops.myinvois.signing import SigningKey, sign_document, strip_signature, verify_document
from malaysia_agent_ops.myinvois.ubl import build_document, serialize, submission_entry
from malaysia_agent_ops.security.vault import Vault
from malaysia_agent_ops.services import audit

from .conftest import EXPECTED_PAYABLE, invoice_payload, make_invoice

ISSUED = datetime(2026, 10, 15, 2, 30, tzinfo=timezone.utc)


# -- invoice model ------------------------------------------------------------------------------


def test_totals_round_half_up_per_line():
    invoice = make_invoice(
        lines=[
            {
                "description": "A",
                "classification_code": "022",
                "quantity": "3",
                "unit_price": "0.335",
                "tax_type": "01",
                "tax_rate": "10",
            },
            {
                "description": "B",
                "classification_code": "022",
                "quantity": "1",
                "unit_price": "10",
                "discount_amount": "2.5",
            },
        ]
    )
    totals = compute_totals(invoice)
    assert [t.line_extension for t in totals.lines] == [Decimal("1.01"), Decimal("7.50")]
    assert totals.tax == Decimal("0.10")
    assert totals.payable == Decimal("8.61")
    assert compute_totals(make_invoice()).payable == EXPECTED_PAYABLE


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("supplier", "tin"), "12345", "TIN"),
        (("supplier", "address", "state_code"), "99", "state code"),
        (("buyer", "id_value"), "12-34", "12 digits"),
        (("buyer", "phone"), "NA", "general TIN"),
        (("supplier", "msic_code"), "123", "5 digits"),
    ],
)
def test_field_validation(path, value, message):
    payload = invoice_payload()
    target = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValidationError, match=message):
        InvoiceInput.model_validate(payload)


def test_notes_require_original_document_and_foreign_currency_requires_rate():
    with pytest.raises(ValidationError, match="original_document"):
        InvoiceInput.model_validate(invoice_payload(document_type="02"))
    with pytest.raises(ValidationError, match="exchange_rate"):
        InvoiceInput.model_validate(invoice_payload(currency="USD"))
    with pytest.raises(ValidationError, match="tax_exemption_reason"):
        InvoiceInput.model_validate(
            invoice_payload(
                lines=[
                    {
                        "description": "x",
                        "classification_code": "022",
                        "quantity": "1",
                        "unit_price": "1",
                        "tax_type": "E",
                    }
                ]
            )
        )


def test_self_billed_issuer_is_buyer():
    invoice = make_invoice(document_type="11")
    assert invoice.issuer_tin == invoice.buyer.tin


# -- UBL ----------------------------------------------------------------------------------------


def test_ubl_structure_and_amounts():
    invoice = make_invoice()
    doc = build_document(invoice, ISSUED)
    inv = doc["Invoice"][0]
    assert doc["_D"].endswith("Invoice-2")
    assert inv["IssueTime"][0]["_"] == "02:30:00Z"
    assert inv["InvoiceTypeCode"][0] == {"_": "01", "listVersionID": "1.0"}
    supplier = inv["AccountingSupplierParty"][0]["Party"][0]
    assert supplier["IndustryClassificationCode"][0] == {"_": "46900", "name": "Wholesale trade"}
    schemes = [i["ID"][0]["schemeID"] for i in supplier["PartyIdentification"]]
    assert schemes == ["TIN", "BRN", "SST", "TTX"]
    assert inv["LegalMonetaryTotal"][0]["PayableAmount"][0] == {"_": 439.0, "currencyID": "MYR"}
    assert inv["InvoiceLine"][1]["TaxTotal"][0]["TaxSubtotal"][0]["Percent"][0]["_"] == 8.0
    assert {s["TaxCategory"][0]["ID"][0]["_"] for s in inv["TaxTotal"][0]["TaxSubtotal"]} == {"06", "02"}


def test_credit_note_references_original():
    invoice = make_invoice(document_type="02", original_document={"code_number": "INV-1", "uuid": "ABC"})
    ref = build_document(invoice, ISSUED)["Invoice"][0]["BillingReference"][0]["InvoiceDocumentReference"][0]
    assert ref == {"ID": [{"_": "INV-1"}], "UUID": [{"_": "ABC"}]}


def test_submission_entry_hash_matches_bytes():
    data = serialize(build_document(make_invoice(), ISSUED))
    entry = submission_entry(data, "INV-1001")
    assert base64.b64decode(entry["document"]) == data
    assert entry["documentHash"] == hashlib.sha256(data).hexdigest()


# -- signing ------------------------------------------------------------------------------------


def _self_signed() -> dict[str, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "Acme Trading Sdn Bhd"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "MY"),
        ]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(ISSUED - timedelta(days=1))
        .not_valid_after(ISSUED + timedelta(days=365))
        .sign(key, hashes.SHA256())
    )
    return {
        "cert_pem": cert.public_bytes(serialization.Encoding.PEM).decode(),
        "key_pem": key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        ).decode(),
    }


def test_sign_and_verify_v11_document():
    doc = build_document(make_invoice(version="1.1"), ISSUED)
    signed = sign_document(doc, SigningKey.from_secret(_self_signed()), ISSUED)
    inv = signed["Invoice"][0]
    assert "UBLExtensions" in inv and inv["Signature"][0]["ID"][0]["_"].endswith("signature:Invoice")
    assert verify_document(signed)
    # Removing the signature gives back exactly the unsigned document.
    assert serialize(strip_signature(signed)) == serialize(doc)
    # Tampering breaks verification.
    inv["LegalMonetaryTotal"][0]["PayableAmount"][0]["_"] = 1.0
    assert not verify_document(signed)


def test_signing_secret_must_be_complete():
    with pytest.raises(NotConfigured):
        SigningKey.from_secret({"cert_pem": "x"})


def test_signed_submission_end_to_end(service, rt, notifier, account, fake):
    from malaysia_agent_ops.services import admin

    from .conftest import SUPPLIER_TIN
    from .test_einvoice_flow import decide

    with rt.db.session() as s:
        admin.store_credential(
            s, rt.vault, account.tenant_id, kind="signing_certificate", environment="preprod", secret=_self_signed()
        )
    drafted = service.draft(
        account.agent, taxpayer_tin=SUPPLIER_TIN, environment="preprod", invoice=make_invoice("SIG-1", version="1.1")
    )
    assert drafted["data"]["warnings"] == []
    decide(
        rt,
        notifier,
        service.submit(account.agent, document_id=drafted["resource_id"])["data"]["approval"]["approval_id"],
    )
    result = service.submit(account.agent, document_id=drafted["resource_id"])
    assert result["status"] == "awaiting_external_event"
    stored = fake.documents[result["data"]["uuid"]]
    assert stored["signed"] and verify_document(json.loads(stored["raw"]))


# -- client -------------------------------------------------------------------------------------


class _Time:
    def __init__(self) -> None:
        self.now = 1000.0
        self.slept: list[float] = []

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds


def _client(fake, t: _Time, max_wait: float = 5.0) -> MyInvoisClient:
    return MyInvoisClient(
        environment="preprod",
        api_base="https://preprod-api.myinvois.hasil.gov.my",
        http=httpx.Client(transport=fake.transport()),
        limiter=RateLimiter(clock=t.clock, sleep=t.sleep),
        tokens=TokenCache(clock=t.clock),
        max_rate_limit_wait=max_wait,
        sleep=t.sleep,
    )


CREDS = ClientCredentials("client-1", "secret-1")


def test_credentials_repr_hides_secret():
    assert "secret-1" not in repr(CREDS)


def test_login_rate_limit_is_respected_across_taxpayers(fake):
    t = _Time()
    client = _client(fake, t, max_wait=0)
    for i in range(12):
        client.access_token(CREDS, f"C1000000{i:03d}0")
    with pytest.raises(RateLimited) as exc:
        client.access_token(CREDS, "C99999999990")
    assert 0 < exc.value.retry_after <= 60
    # Cached tokens do not count against the login limit.
    client.access_token(CREDS, "C10000000000")


def test_token_refreshes_before_expiry_and_after_401(fake):
    t = _Time()
    client = _client(fake, t)
    first = client.access_token(CREDS, "C25845632020")
    assert client.access_token(CREDS, "C25845632020") == first
    t.now += 3600 - 200  # inside the refresh margin
    second = client.access_token(CREDS, "C25845632020")
    assert second != first
    fake.tokens.pop(second)  # server-side revocation: the next call gets a 401, logs in again and succeeds
    assert (
        client.validate_tin(CREDS, "C25845632020", tin="C10987654320", id_type="BRN", id_value="202001234567") is True
    )
    assert len(fake.logins) == 3


def test_429_retry_after_is_honoured(fake):
    t = _Time()
    client = _client(fake, t)
    fake.registered_tins["C10987654320"] = ("BRN", "202001234567")
    fake.throttle_next = 1
    assert client.validate_tin(CREDS, None, tin="C10987654320", id_type="BRN", id_value="202001234567") is True
    assert t.slept == [1.0]
    fake.throttle_next = 2
    with pytest.raises(RateLimited):
        client.validate_tin(CREDS, None, tin="C10987654320", id_type="BRN", id_value="202001234567")


def test_bad_credentials_do_not_echo_secret(fake):
    client = _client(fake, _Time())
    with pytest.raises(Exception) as exc:
        client.access_token(ClientCredentials("client-1", "wrong"), None)
    assert "wrong" not in str(exc.value) and "wrong" not in str(getattr(exc.value, "details", ""))


# -- consolidation ------------------------------------------------------------------------------


def test_consolidation_groups_lines_when_over_limit():
    supplier = make_invoice().supplier
    receipts = [
        consolidation.Receipt(reference=f"R{i:05d}", issued_on=date(2026, 9, 1 + i % 28), amount=Decimal("1"))
        for i in range(2500)
    ]
    result = consolidation.plan(month="2026-09", receipts=receipts, supplier=supplier, code_number="C-1")
    assert len(result.invoice.lines) <= consolidation.MAX_LINES
    assert compute_totals(result.invoice).payable == Decimal("2500.00")
    with pytest.raises(ValueError, match="outside"):
        consolidation.plan(month="2026-08", receipts=receipts[:1], supplier=supplier, code_number="C-2")


# -- audit and vault ----------------------------------------------------------------------------


def test_audit_chain_detects_tampering(rt, account):
    with rt.db.session() as s:
        assert audit.verify_chain(s, account.tenant_id)["valid"] is True
        s.execute(text("UPDATE audit_events SET outcome = 'forged' WHERE id = (SELECT MIN(id) FROM audit_events)"))
    with rt.db.session() as s:
        result = audit.verify_chain(s, account.tenant_id)
        assert result["valid"] is False and result["first_bad_event_id"]


def test_audit_redacts_secret_keys(rt, account):
    with rt.db.session() as s:
        event = audit.record(
            s, tenant_id=account.tenant_id, actor="t", action="x", outcome="ok", details={"client_secret": "s", "ok": 1}
        )
        assert event.details == {"client_secret": "[redacted]", "ok": 1}


def test_vault_round_trip_and_rotation():
    old, new = Vault.generate_key(), Vault.generate_key()
    sealed = Vault(old).encrypt({"client_secret": "s"})
    assert 's"' not in sealed
    assert Vault(f"{new},{old}").decrypt(sealed) == {"client_secret": "s"}
    with pytest.raises(NotConfigured):
        Vault(new).decrypt(sealed)
    with pytest.raises(NotConfigured):
        Vault(None).encrypt({})
