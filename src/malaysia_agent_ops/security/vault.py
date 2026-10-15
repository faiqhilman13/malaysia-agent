"""Credential vault: encrypts secrets at rest with Fernet (AES-128-CBC + HMAC-SHA256).

Secrets go in through the admin CLI and come out only inside the service layer, at the moment an
upstream call needs them. They are never accepted as tool arguments or returned in tool results.
Swap this class for a KMS-backed one in production; the interface is two methods.
"""

from __future__ import annotations

import json
from typing import Any

from cryptography.fernet import Fernet, InvalidToken, MultiFernet

from ..errors import NotConfigured


class Vault:
    def __init__(self, keys: str | None) -> None:
        parsed = [k.strip() for k in (keys or "").split(",") if k.strip()]
        self._fernet = MultiFernet([Fernet(k.encode()) for k in parsed]) if parsed else None

    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode()

    @property
    def configured(self) -> bool:
        return self._fernet is not None

    def encrypt(self, secret: dict[str, Any]) -> str:
        return self._require().encrypt(json.dumps(secret).encode()).decode()

    def decrypt(self, ciphertext: str) -> dict[str, Any]:
        try:
            return json.loads(self._require().decrypt(ciphertext.encode()))
        except InvalidToken as exc:
            raise NotConfigured("Stored credential cannot be decrypted with the configured vault keys.") from exc

    def _require(self) -> MultiFernet:
        if self._fernet is None:
            raise NotConfigured("MYOPS_VAULT_KEYS is not set; generate one with `myops vault generate-key`.")
        return self._fernet
