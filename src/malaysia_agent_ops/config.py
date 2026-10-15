from __future__ import annotations

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, read from MYOPS_* environment variables (or a .env file)."""

    model_config = SettingsConfigDict(env_prefix="MYOPS_", env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./myops.db"
    # Fernet key(s) for the credential vault. Comma-separated; the first encrypts, all decrypt (rotation).
    vault_keys: SecretStr | None = None
    # Public URL of this service. Used for approval links and OAuth protected-resource metadata.
    public_base_url: str = "http://127.0.0.1:8080"

    myinvois_preprod_api_base: str = "https://preprod-api.myinvois.hasil.gov.my"
    myinvois_production_api_base: str = "https://api.myinvois.hasil.gov.my"
    myinvois_preprod_portal_base: str = "https://preprod.myinvois.hasil.gov.my"
    myinvois_production_portal_base: str = "https://myinvois.hasil.gov.my"
    myinvois_timeout_seconds: float = 30.0
    # Longest the client will sleep for a rate-limit slot before giving up and reporting it.
    myinvois_max_rate_limit_wait_seconds: float = 5.0

    approval_ttl_minutes: int = 24 * 60

    # Optional external OAuth 2.1 authorization server (e.g. Auth0, Keycloak, WorkOS) for MCP and REST.
    # API keys work without it.
    oauth_issuer: str | None = None
    oauth_audience: str | None = None
    oauth_jwks_url: str | None = None
    oauth_tenant_claim: str = "myops_tenant"
    oauth_role_claim: str = "myops_role"

    # Extra Host header values accepted by the MCP endpoint (DNS-rebinding protection), e.g. "api.example.com".
    mcp_allowed_hosts: list[str] = []


@lru_cache
def get_settings() -> Settings:
    return Settings()
