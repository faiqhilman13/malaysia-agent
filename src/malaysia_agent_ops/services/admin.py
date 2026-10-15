"""Account setup: tenants, users, API keys, taxpayers, mandates and credentials. Used by the admin CLI."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import ApiKey, Appointment, Credential, Taxpayer, Tenant, User, utcnow
from ..errors import InvalidInput, NotFound
from ..myinvois import codes
from ..myinvois.invoice import is_valid_tin, normalise_tin
from ..security.auth import ROLES, generate_api_key, hash_key
from ..security.vault import Vault
from . import audit

ADMIN_ACTOR = "admin-cli"


def create_tenant(s: Session, name: str, settings: dict[str, Any] | None = None) -> Tenant:
    tenant = Tenant(name=name, settings=settings or {})
    s.add(tenant)
    s.flush()
    audit.record(
        s, tenant_id=tenant.id, actor=ADMIN_ACTOR, action="tenant.created", outcome="ok", details={"name": name}
    )
    return tenant


def _tenant(s: Session, tenant_id: str) -> Tenant:
    tenant = s.get(Tenant, tenant_id)
    if tenant is None:
        raise NotFound(f"Tenant {tenant_id} not found.")
    return tenant


def create_user(
    s: Session, tenant_id: str, *, email: str, role: str, name: str | None = None, phone: str | None = None
) -> User:
    _tenant(s, tenant_id)
    if role not in ("admin", "approver", "member"):
        raise InvalidInput("role must be admin, approver or member")
    user = User(tenant_id=tenant_id, email=email.strip().lower(), role=role, display_name=name, phone=phone)
    s.add(user)
    s.flush()
    audit.record(
        s,
        tenant_id=tenant_id,
        actor=ADMIN_ACTOR,
        action="user.created",
        outcome="ok",
        resource_type="user",
        resource_id=user.id,
        details={"role": role},
    )
    return user


def create_api_key(
    s: Session, tenant_id: str, *, role: str, name: str, user_id: str | None = None
) -> tuple[ApiKey, str]:
    """Returns the record and the raw key. The raw key is not stored and cannot be shown again."""
    _tenant(s, tenant_id)
    if role not in ROLES:
        raise InvalidInput(f"role must be one of {', '.join(ROLES)}")
    if role in ("approver", "admin") and user_id is None:
        raise InvalidInput("approver and admin keys must belong to a user")
    if user_id is not None:
        user = s.get(User, user_id)
        if user is None or user.tenant_id != tenant_id:
            raise NotFound("User not found in this tenant.")
    raw, prefix = generate_api_key()
    record = ApiKey(tenant_id=tenant_id, user_id=user_id, role=role, name=name, prefix=prefix, key_hash=hash_key(raw))
    s.add(record)
    s.flush()
    audit.record(
        s,
        tenant_id=tenant_id,
        actor=ADMIN_ACTOR,
        action="api_key.created",
        outcome="ok",
        resource_type="api_key",
        resource_id=record.id,
        details={"role": role, "prefix": prefix},
    )
    return record, raw


def revoke_api_key(s: Session, key_id: str) -> None:
    record = s.get(ApiKey, key_id)
    if record is None:
        raise NotFound("API key not found.")
    record.revoked_at = utcnow()
    audit.record(
        s,
        tenant_id=record.tenant_id,
        actor=ADMIN_ACTOR,
        action="api_key.revoked",
        outcome="ok",
        resource_type="api_key",
        resource_id=record.id,
    )


def add_taxpayer(s: Session, tenant_id: str, *, tin: str, id_type: str, id_value: str, name: str) -> Taxpayer:
    _tenant(s, tenant_id)
    tin = normalise_tin(tin)
    if not is_valid_tin(tin):
        raise InvalidInput(f"{tin} is not a valid TIN format")
    if id_type not in codes.ID_TYPES:
        raise InvalidInput("id_type must be BRN, NRIC, PASSPORT or ARMY")
    taxpayer = Taxpayer(tenant_id=tenant_id, tin=tin, id_type=id_type, id_value=id_value, name=name)
    s.add(taxpayer)
    s.flush()
    audit.record(
        s,
        tenant_id=tenant_id,
        actor=ADMIN_ACTOR,
        action="taxpayer.added",
        outcome="ok",
        resource_type="taxpayer",
        resource_id=taxpayer.id,
        details={"tin": tin},
    )
    return taxpayer


def taxpayer_by_tin(s: Session, tenant_id: str, tin: str) -> Taxpayer:
    taxpayer = s.scalar(select(Taxpayer).where(Taxpayer.tenant_id == tenant_id, Taxpayer.tin == normalise_tin(tin)))
    if taxpayer is None:
        raise NotFound(f"Taxpayer {tin} not found in this tenant.")
    return taxpayer


def add_appointment(
    s: Session,
    tenant_id: str,
    *,
    taxpayer_tin: str,
    mode: str,
    permissions: list[str],
    valid_from: datetime,
    valid_to: datetime,
    evidence: str | None = None,
) -> Appointment:
    taxpayer = taxpayer_by_tin(s, tenant_id, taxpayer_tin)
    if mode not in ("intermediary", "self"):
        raise InvalidInput("mode must be intermediary or self")
    unknown = set(permissions) - set(codes.PERMISSIONS)
    if unknown:
        raise InvalidInput(f"unknown permissions: {', '.join(sorted(unknown))}")
    if valid_to <= valid_from:
        raise InvalidInput("valid_to must be after valid_from")
    appointment = Appointment(
        tenant_id=tenant_id,
        taxpayer_id=taxpayer.id,
        mode=mode,
        permissions=sorted(set(permissions)),
        valid_from=valid_from,
        valid_to=valid_to,
        evidence=evidence,
    )
    s.add(appointment)
    s.flush()
    audit.record(
        s,
        tenant_id=tenant_id,
        actor=ADMIN_ACTOR,
        action="appointment.added",
        outcome="ok",
        resource_type="appointment",
        resource_id=appointment.id,
        details={
            "tin": taxpayer.tin,
            "mode": mode,
            "permissions": appointment.permissions,
            "valid_to": valid_to.isoformat(),
        },
    )
    return appointment


def store_credential(
    s: Session,
    vault: Vault,
    tenant_id: str,
    *,
    kind: str,
    environment: str,
    secret: dict[str, Any],
    taxpayer_tin: str | None = None,
) -> Credential:
    _tenant(s, tenant_id)
    if kind not in ("myinvois_client", "signing_certificate"):
        raise InvalidInput("kind must be myinvois_client or signing_certificate")
    if environment not in ("preprod", "production"):
        raise InvalidInput("environment must be preprod or production")
    if kind == "myinvois_client" and not {"client_id", "client_secret"} <= secret.keys():
        raise InvalidInput("a MyInvois credential needs client_id and client_secret")
    taxpayer_id = taxpayer_by_tin(s, tenant_id, taxpayer_tin).id if taxpayer_tin else None
    credential = Credential(
        tenant_id=tenant_id,
        taxpayer_id=taxpayer_id,
        kind=kind,
        environment=environment,
        ciphertext=vault.encrypt(secret),
    )
    s.add(credential)
    s.flush()
    audit.record(
        s,
        tenant_id=tenant_id,
        actor=ADMIN_ACTOR,
        action="credential.stored",
        outcome="ok",
        resource_type="credential",
        resource_id=credential.id,
        details={"kind": kind, "environment": environment, "taxpayer_tin": taxpayer_tin},
    )
    return credential


def set_approval_policy(s: Session, tenant_id: str, policy: dict[str, Any]) -> Tenant:
    tenant = _tenant(s, tenant_id)
    allowed = {"submit", "cancel", "reject", "auto_approve_submit_max", "ttl_minutes"}
    unknown = set(policy) - allowed
    if unknown:
        raise InvalidInput(f"unknown policy keys: {', '.join(sorted(unknown))}")
    tenant.settings = {**(tenant.settings or {}), "approval_policy": policy}
    audit.record(s, tenant_id=tenant_id, actor=ADMIN_ACTOR, action="approval_policy.set", outcome="ok", details=policy)
    return tenant
