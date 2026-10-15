"""Who is calling: API keys (hashed at rest) or JWTs from an external OAuth 2.1 server.

Roles:
- agent: may call e-invoice tools. Can request approvals but never decide them.
- approver: a human who decides approvals. Must be bound to a user.
- admin: manages the tenant.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Any

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import Settings
from ..db import ApiKey, utcnow
from ..errors import Unauthenticated

ROLES = ("agent", "approver", "admin")
KEY_PREFIX = "myops_"


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    # Stable identifier recorded in the audit log and on approvals, e.g. "key:<id>" or "oauth:<sub>".
    subject: str
    role: str
    user_id: str | None = None

    @property
    def is_human(self) -> bool:
        return self.role in ("approver", "admin") and self.user_id is not None


def hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_api_key() -> tuple[str, str]:
    """Returns (raw_key, prefix). Show the raw key once; store only its hash."""
    raw = KEY_PREFIX + secrets.token_urlsafe(32)
    return raw, raw[:14]


def authenticate_api_key(session: Session, raw: str) -> Principal:
    if not raw.startswith(KEY_PREFIX):
        raise Unauthenticated("Not an API key.")
    record = session.scalar(select(ApiKey).where(ApiKey.key_hash == hash_key(raw)))
    if record is None or record.revoked_at is not None:
        raise Unauthenticated("Unknown or revoked API key.")
    record.last_used_at = utcnow()
    return Principal(tenant_id=record.tenant_id, subject=f"key:{record.id}", role=record.role, user_id=record.user_id)


class JwtVerifier:
    """Verifies access tokens from an external authorization server via its JWKS."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._jwks = jwt.PyJWKClient(settings.oauth_jwks_url) if settings.oauth_jwks_url else None

    @property
    def enabled(self) -> bool:
        return self._jwks is not None and bool(self.settings.oauth_issuer)

    def verify(self, token: str) -> Principal:
        if not self.enabled:
            raise Unauthenticated("OAuth is not configured on this server.")
        assert self._jwks is not None
        try:
            signing_key = self._jwks.get_signing_key_from_jwt(token)
            claims: dict[str, Any] = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256", "PS256"],
                audience=self.settings.oauth_audience,
                issuer=self.settings.oauth_issuer,
                options={"require": ["exp", "iss", "sub"]},
            )
        except jwt.PyJWTError as exc:
            raise Unauthenticated(f"Invalid access token: {exc}") from exc
        tenant_id = claims.get(self.settings.oauth_tenant_claim)
        role = claims.get(self.settings.oauth_role_claim, "agent")
        if not tenant_id or role not in ROLES:
            raise Unauthenticated("Access token lacks a tenant or a valid role claim.")
        user_id = claims.get("myops_user")
        return Principal(tenant_id=str(tenant_id), subject=f"oauth:{claims['sub']}", role=role, user_id=user_id)


def authenticate_bearer(session: Session, token: str, jwt_verifier: JwtVerifier | None) -> Principal:
    if token.startswith(KEY_PREFIX):
        return authenticate_api_key(session, token)
    if jwt_verifier is not None and jwt_verifier.enabled:
        return jwt_verifier.verify(token)
    raise Unauthenticated("Unrecognised bearer token.")
