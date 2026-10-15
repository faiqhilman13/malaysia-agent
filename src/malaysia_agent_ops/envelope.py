"""The response envelope every tool and REST call returns.

Agents read `status` to decide whether they can proceed, `next_action` for what to do next, and
`blocking_reason` for why they cannot. Kept from v0, where it was the best part of the design.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from .errors import OpsError

Status = Literal[
    "success",
    # A human must approve out of band. Poll approval_get_status, then retry the same call.
    "awaiting_human_approval",
    # Waiting on MyInvois (e.g. validation in progress). Poll the suggested status tool.
    "awaiting_external_event",
    # Cannot proceed without a change the agent cannot make itself (credentials, mandate, expired window).
    "blocked",
    # The input is wrong. Fix the fields listed in data.issues and retry.
    "invalid",
    "error",
]


def envelope(
    status: Status,
    *,
    data: dict[str, Any] | None = None,
    next_action: str | None = None,
    blocking_reason: str | None = None,
    resource_id: str | None = None,
    source_system: str = "myops",
) -> dict[str, Any]:
    return {
        "status": status,
        "next_action": next_action,
        "blocking_reason": blocking_reason,
        "source_system": source_system,
        "resource_id": resource_id,
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "data": data or {},
    }


_ERROR_STATUS: dict[str, Status] = {
    "invalid_input": "invalid",
    "not_configured": "blocked",
    "forbidden": "blocked",
    "rate_limited": "blocked",
}


def error_envelope(exc: OpsError) -> dict[str, Any]:
    status = _ERROR_STATUS.get(exc.code, "error")
    data: dict[str, Any] = {"error_code": exc.code, **exc.details}
    retry_after = getattr(exc, "retry_after", None)
    next_action = f"retry after {retry_after:.0f} seconds" if retry_after else None
    return envelope(status, data=data, blocking_reason=exc.message, next_action=next_action)
