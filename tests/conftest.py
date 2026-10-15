from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pytest

from malaysia_agent_ops.config import Settings
from malaysia_agent_ops.db import Base
from malaysia_agent_ops.myinvois.client import RateLimiter, TokenCache
from malaysia_agent_ops.myinvois.invoice import InvoiceInput
from malaysia_agent_ops.runtime import Runtime
from malaysia_agent_ops.security.auth import Principal, authenticate_api_key
from malaysia_agent_ops.security.vault import Vault
from malaysia_agent_ops.services import admin
from malaysia_agent_ops.services.einvoice import EInvoiceService
from malaysia_agent_ops.services.notify import MemoryNotifier

from .fake_myinvois import FakeMyInvois

SUPPLIER_TIN = "C25845632020"
BUYER_TIN = "C10987654320"
OTHER_TIN = "C55555555550"


class Clock:
    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **delta: float) -> None:
        self.now += timedelta(**delta)


@dataclass
class Account:
    tenant_id: str
    agent: Principal
    agent_key: str
    approver: Principal
    approver_key: str
    approver_user_id: str
    admin_key: str


@pytest.fixture
def clock() -> Clock:
    return Clock(datetime(2026, 10, 15, 2, 0, tzinfo=timezone.utc))


@pytest.fixture
def fake(clock: Clock) -> FakeMyInvois:
    fake = FakeMyInvois(clock=clock)
    fake.registered_tins[BUYER_TIN] = ("BRN", "202001234567")
    return fake


@pytest.fixture
def notifier() -> MemoryNotifier:
    return MemoryNotifier()


@pytest.fixture
def rt(tmp_path: Path, fake: FakeMyInvois, notifier: MemoryNotifier, clock: Clock) -> Iterator[Runtime]:
    key = Vault.generate_key()
    # Set MYOPS_TEST_DATABASE_URL (e.g. postgresql+psycopg://...) to run the suite against Postgres.
    database_url = os.environ.get("MYOPS_TEST_DATABASE_URL") or f"sqlite:///{tmp_path / 'test.db'}"
    settings = Settings(
        database_url=database_url,
        vault_keys=key,
        public_base_url="https://ops.example.my",
        myinvois_max_rate_limit_wait_seconds=2.0,
        _env_file=None,
    )
    runtime = Runtime.from_settings(settings, notifier=notifier)
    runtime.clock = clock
    runtime.http = httpx.Client(transport=fake.transport())
    runtime.limiter = RateLimiter(sleep=lambda _s: None)
    runtime.tokens = TokenCache()
    Base.metadata.drop_all(runtime.db.engine)
    runtime.db.create_all()
    yield runtime
    runtime.db.engine.dispose()


@pytest.fixture
def service(rt: Runtime) -> EInvoiceService:
    return EInvoiceService(rt)


@pytest.fixture
def account(rt: Runtime, clock: Clock) -> Account:
    with rt.db.session() as s:
        tenant = admin.create_tenant(s, "Kira Bookkeeping")
        approver = admin.create_user(s, tenant.id, email="owner@acme.example", role="approver", phone="+60123456789")
        admin_user = admin.create_user(s, tenant.id, email="admin@kira.example", role="admin")
        _, agent_key = admin.create_api_key(s, tenant.id, role="agent", name="claude")
        _, approver_key = admin.create_api_key(s, tenant.id, role="approver", name="owner", user_id=approver.id)
        _, admin_key = admin.create_api_key(s, tenant.id, role="admin", name="admin", user_id=admin_user.id)
        admin.add_taxpayer(
            s, tenant.id, tin=SUPPLIER_TIN, id_type="BRN", id_value="201901234567", name="Acme Trading Sdn Bhd"
        )
        admin.add_appointment(
            s,
            tenant.id,
            taxpayer_tin=SUPPLIER_TIN,
            mode="intermediary",
            permissions=["view_documents", "submit_documents", "cancel_documents", "reject_documents"],
            valid_from=clock() - timedelta(days=1),
            valid_to=clock() + timedelta(days=365),
            evidence="Appointed in MyInvois portal by director",
        )
        for env in ("preprod", "production"):
            admin.store_credential(
                s,
                rt.vault,
                tenant.id,
                kind="myinvois_client",
                environment=env,
                secret={"client_id": "client-1", "client_secret": "secret-1"},
            )
        tenant_id, approver_id = tenant.id, approver.id
    with rt.db.session() as s:
        agent = authenticate_api_key(s, agent_key)
        approver_principal = authenticate_api_key(s, approver_key)
    return Account(tenant_id, agent, agent_key, approver_principal, approver_key, approver_id, admin_key)


def invoice_payload(code: str = "INV-1001", **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code_number": code,
        "supplier": {
            "name": "Acme Trading Sdn Bhd",
            "tin": SUPPLIER_TIN,
            "id_type": "BRN",
            "id_value": "201901234567",
            "address": {
                "lines": ["Lot 5, Jalan Ampang"],
                "city": "Kuala Lumpur",
                "postcode": "50450",
                "state_code": "14",
            },
            "phone": "+60321234567",
            "email": "billing@acme.example",
            "msic_code": "46900",
            "business_activity": "Wholesale trade",
        },
        "buyer": {
            "name": "Berjaya Kedai Runcit Sdn Bhd",
            "tin": BUYER_TIN,
            "id_type": "BRN",
            "id_value": "202001234567",
            "address": {"lines": ["No 2, Jalan SS2/24"], "city": "Petaling Jaya", "state_code": "10"},
            "phone": "+60378765432",
        },
        "lines": [
            {
                "description": "Rice 10kg",
                "classification_code": "022",
                "quantity": "10",
                "unit_price": "38.50",
                "tax_type": "06",
            },
            {
                "description": "Delivery",
                "classification_code": "022",
                "quantity": "1",
                "unit_price": "50",
                "tax_type": "02",
                "tax_rate": "8",
            },
        ],
    }
    payload.update(overrides)
    return payload


def make_invoice(code: str = "INV-1001", **overrides: Any) -> InvoiceInput:
    return InvoiceInput.model_validate(invoice_payload(code, **overrides))


EXPECTED_PAYABLE = Decimal("439.00")  # 385.00 + 50.00 + 4.00 service tax
