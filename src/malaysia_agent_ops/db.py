"""Database models and session handling.

Postgres in production, SQLite for local development and tests. Schema changes go through Alembic
migrations in `migrations/`.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


def new_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes; everything is stored in UTC, so attach the zone back."""
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSON, list[str]: JSON}


class Tenant(Base):
    """A customer account: a bookkeeping firm, a software vendor, or a business acting for itself."""

    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    # Approval policy and other per-tenant options. See services.approvals.ApprovalPolicy.
    settings: Mapped[dict[str, Any]] = mapped_column(default=dict)
    # Head of this tenant's audit hash chain. Updated under a row lock with every audit event.
    audit_head: Mapped[str] = mapped_column(String(64), default="0" * 64)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class User(Base):
    """A human at a tenant. Approvers receive approval links on their own channels."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    email: Mapped[str] = mapped_column(String(320))
    display_name: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(32))
    # admin | approver | member
    role: Mapped[str] = mapped_column(String(20), default="member")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (UniqueConstraint("tenant_id", "email"),)


class ApiKey(Base):
    """A bearer credential. Only a SHA-256 hash is stored; the raw key is shown once at creation."""

    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(200))
    # agent | approver | admin
    role: Mapped[str] = mapped_column(String(20))
    prefix: Mapped[str] = mapped_column(String(24), index=True)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Taxpayer(Base):
    """A business the tenant may act for (or the tenant itself)."""

    __tablename__ = "taxpayers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    tin: Mapped[str] = mapped_column(String(20))
    id_type: Mapped[str] = mapped_column(String(10))
    id_value: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (UniqueConstraint("tenant_id", "tin"),)


class Appointment(Base):
    """The mandate: what the tenant may do for a taxpayer, and until when.

    `intermediary` mirrors the MyInvois intermediary appointment a director makes in the portal; the tenant's
    own Client ID logs in with an `onbehalfof` header. `self` means the tenant is the taxpayer and uses the
    taxpayer's own ERP credentials.
    """

    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    taxpayer_id: Mapped[str] = mapped_column(ForeignKey("taxpayers.id"), index=True)
    mode: Mapped[str] = mapped_column(String(20))
    # Subset of services.einvoice.PERMISSIONS
    permissions: Mapped[list[str]] = mapped_column(default=list)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    valid_to: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # Free text describing the evidence of the appointment (e.g. "MyInvois portal, appointed by director X").
    evidence: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Credential(Base):
    """An encrypted secret: a MyInvois Client ID/secret pair or a signing certificate."""

    __tablename__ = "credentials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    # Null for the tenant's own intermediary credential; set for a taxpayer's own (`self` mode) credential.
    taxpayer_id: Mapped[str | None] = mapped_column(ForeignKey("taxpayers.id"))
    # myinvois_client | signing_certificate
    kind: Mapped[str] = mapped_column(String(40))
    # preprod | production
    environment: Mapped[str] = mapped_column(String(20))
    ciphertext: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Document(Base):
    """An e-invoice (or note) prepared by an agent, and its MyInvois lifecycle."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    taxpayer_id: Mapped[str] = mapped_column(ForeignKey("taxpayers.id"), index=True)
    environment: Mapped[str] = mapped_column(String(20))
    document_type: Mapped[str] = mapped_column(String(4))
    version: Mapped[str] = mapped_column(String(8))
    code_number: Mapped[str] = mapped_column(String(50))
    # draft | submitted | valid | invalid | cancelled | failed
    status: Mapped[str] = mapped_column(String(20), default="draft")
    input: Mapped[dict[str, Any]] = mapped_column()
    ubl_json: Mapped[str] = mapped_column(Text)
    # SHA-256 of the unsigned UBL. Approvals bind to this, so any change to the document voids them.
    payload_hash: Mapped[str] = mapped_column(String(64))
    currency: Mapped[str] = mapped_column(String(3))
    payable_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    buyer_tin: Mapped[str] = mapped_column(String(20))
    buyer_name: Mapped[str] = mapped_column(String(300))
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    submission_uid: Mapped[str | None] = mapped_column(String(64), index=True)
    uuid: Mapped[str | None] = mapped_column(String(64), index=True)
    long_id: Mapped[str | None] = mapped_column(String(128))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    errors: Mapped[list[str]] = mapped_column(default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    __table_args__ = (UniqueConstraint("taxpayer_id", "environment", "code_number"),)


class Approval(Base):
    """A human decision on one exact payload. Single use, expiring, decided outside the agent's reach."""

    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    # einvoice.submit | einvoice.cancel | einvoice.reject
    action: Mapped[str] = mapped_column(String(40))
    resource_id: Mapped[str] = mapped_column(String(64))
    payload_hash: Mapped[str] = mapped_column(String(64))
    summary: Mapped[dict[str, Any]] = mapped_column()
    # pending | approved | rejected | consumed (expiry is computed from expires_at)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    requested_by: Mapped[str] = mapped_column(String(100))
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # user_id -> SHA-256 of the one-time decision token sent to that approver out of band.
    # Raw tokens are never stored, never returned by the API, and never reach the agent.
    token_hashes: Mapped[dict[str, Any]] = mapped_column(default=dict)
    decided_by: Mapped[str | None] = mapped_column(String(100))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision_note: Mapped[str | None] = mapped_column(Text)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"))
    scope: Mapped[str] = mapped_column(String(60))
    key: Mapped[str] = mapped_column(String(200))
    request_hash: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (UniqueConstraint("tenant_id", "scope", "key"),)


class AuditEvent(Base):
    """Append-only, hash-chained per tenant. The Postgres migration also blocks UPDATE and DELETE."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actor: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(60))
    resource_type: Mapped[str | None] = mapped_column(String(40))
    resource_id: Mapped[str | None] = mapped_column(String(64))
    outcome: Mapped[str] = mapped_column(String(40))
    details: Mapped[dict[str, Any]] = mapped_column(default=dict)
    prev_hash: Mapped[str] = mapped_column(String(64))
    hash: Mapped[str] = mapped_column(String(64))


def make_engine(database_url: str) -> Engine:
    if database_url.startswith("sqlite"):
        engine = create_engine(database_url, connect_args={"check_same_thread": False})

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_connection: Any, _record: Any) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine
    return create_engine(database_url, pool_pre_ping=True)


class Database:
    def __init__(self, database_url: str) -> None:
        self.engine = make_engine(database_url)
        self._sessions = sessionmaker(self.engine, expire_on_commit=False)

    def create_all(self) -> None:
        """For tests and throwaway local databases. Real deployments run `myops db upgrade`."""
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self._sessions()
        try:
            yield session
            session.commit()
        except BaseException:
            session.rollback()
            raise
        finally:
            session.close()
