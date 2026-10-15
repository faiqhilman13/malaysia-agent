"""Keep secrets and avoidable personal data out of logs and tool results.

Tool results go to whatever AI client the business uses, often hosted outside Malaysia, so PDPA
cross-border rules apply to anything returned. Return what the agent needs to act, not more.
"""

from __future__ import annotations

import re
from typing import Any

_SECRET_KEYS = re.compile(r"secret|password|token|authorization|api_key|private_key|pkcs12", re.I)
_EMAIL = re.compile(r"^([^@]{1,2})[^@]*(@.+)$")


def mask_email(value: str | None) -> str | None:
    if not value:
        return value
    return _EMAIL.sub(r"\1***\2", value)


def mask_phone(value: str | None) -> str | None:
    if not value or len(value) < 5:
        return value
    return value[:3] + "*" * (len(value) - 5) + value[-2:]


def mask_id(value: str | None) -> str | None:
    """Mask NRIC / passport numbers; keep BRNs and placeholder values readable."""
    if not value or value.upper() == "NA" or len(value) < 6:
        return value
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: ("[redacted]" if _SECRET_KEYS.search(str(k)) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value
