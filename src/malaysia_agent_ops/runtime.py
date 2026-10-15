"""Wires settings, database, vault, MyInvois clients and notifier together. One per process."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from functools import cached_property

import httpx

from .config import Settings, get_settings
from .db import Database, utcnow
from .errors import InvalidInput
from .myinvois.client import MyInvoisClient, RateLimiter, TokenCache
from .security.auth import JwtVerifier
from .security.vault import Vault
from .services.notify import LogNotifier, Notifier

ENVIRONMENTS = ("preprod", "production")


@dataclass
class Runtime:
    settings: Settings
    db: Database
    vault: Vault
    notifier: Notifier
    clock: Callable[[], datetime] = utcnow
    # Injected in tests to point MyInvois calls at a fake.
    http: httpx.Client | None = None
    limiter: RateLimiter = field(default_factory=RateLimiter)
    tokens: TokenCache = field(default_factory=TokenCache)
    _clients: dict[str, MyInvoisClient] = field(default_factory=dict)

    @classmethod
    def from_settings(cls, settings: Settings | None = None, *, notifier: Notifier | None = None) -> Runtime:
        settings = settings or get_settings()
        return cls(
            settings=settings,
            db=Database(settings.database_url),
            vault=Vault(settings.vault_keys.get_secret_value() if settings.vault_keys else None),
            notifier=notifier or LogNotifier(),
        )

    @cached_property
    def jwt(self) -> JwtVerifier:
        return JwtVerifier(self.settings)

    def myinvois(self, environment: str) -> MyInvoisClient:
        if environment not in ENVIRONMENTS:
            raise InvalidInput("environment must be preprod or production")
        if environment not in self._clients:
            base = (
                self.settings.myinvois_production_api_base
                if environment == "production"
                else self.settings.myinvois_preprod_api_base
            )
            self._clients[environment] = MyInvoisClient(
                environment=environment,
                api_base=base,
                http=self.http,
                limiter=self.limiter,
                tokens=self.tokens,
                max_rate_limit_wait=self.settings.myinvois_max_rate_limit_wait_seconds,
                timeout=self.settings.myinvois_timeout_seconds,
            )
        return self._clients[environment]

    def portal_base(self, environment: str) -> str:
        return (
            self.settings.myinvois_production_portal_base
            if environment == "production"
            else self.settings.myinvois_preprod_portal_base
        ).rstrip("/")
