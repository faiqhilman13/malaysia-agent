from __future__ import annotations

from typing import Any


class OpsError(Exception):
    """Base error. `code` is stable and machine-readable; `message` is for humans and agents."""

    code = "error"
    http_status = 400

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidInput(OpsError):
    code = "invalid_input"
    http_status = 422


class NotFound(OpsError):
    code = "not_found"
    http_status = 404


class Forbidden(OpsError):
    code = "forbidden"
    http_status = 403


class Unauthenticated(OpsError):
    code = "unauthenticated"
    http_status = 401


class Conflict(OpsError):
    code = "conflict"
    http_status = 409


class NotConfigured(OpsError):
    """A required credential, certificate or setting is missing. Never retried automatically."""

    code = "not_configured"
    http_status = 412


class UpstreamError(OpsError):
    """MyInvois (or another upstream) returned an error or could not be reached."""

    code = "upstream_error"
    http_status = 502

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retry_after: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details=details)
        self.status_code = status_code
        self.retry_after = retry_after


class RateLimited(UpstreamError):
    code = "rate_limited"
    http_status = 429
