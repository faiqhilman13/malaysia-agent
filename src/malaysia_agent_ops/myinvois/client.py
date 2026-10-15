"""MyInvois API client: one cached token per (Client ID, taxpayer), per-endpoint rate limits, Retry-After.

Rate limits apply per Client ID. An intermediary serving many taxpayers shares one login budget
(12/minute), so tokens are cached per taxpayer and reused until shortly before they expire.

The limiter and token cache are in-process. Running several workers needs a shared store (e.g.
Redis) behind the same interfaces.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Any

import httpx

from ..errors import RateLimited, UpstreamError

# Requests per minute per Client ID. Login, submit, get-submission, cancel, reject and search-documents
# are from the SDK integration-practices page. The others are conservative assumptions until confirmed.
RATE_LIMITS: dict[str, int] = {
    "login": 12,
    "submit": 100,
    "get_submission": 300,
    "cancel": 12,
    "reject": 12,
    "search_documents": 12,
    "validate_tin": 60,  # assumed
    "search_tin": 60,  # assumed
    "document_details": 60,  # assumed
    "document_types": 12,  # assumed
}
TOKEN_REFRESH_MARGIN_SECONDS = 300


@dataclass(frozen=True)
class ClientCredentials:
    client_id: str
    client_secret: str

    def __repr__(self) -> str:  # never print the secret
        return f"ClientCredentials(client_id={self.client_id!r}, client_secret='***')"


class RateLimiter:
    """Sliding one-minute window per key. Sleeps briefly for a slot, otherwise raises RateLimited."""

    def __init__(
        self,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._clock = clock
        self._sleep = sleep
        self._windows: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def acquire(self, key: str, limit: int, max_wait: float) -> None:
        while True:
            with self._lock:
                now = self._clock()
                window = self._windows.setdefault(key, deque())
                while window and window[0] <= now - 60:
                    window.popleft()
                if len(window) < limit:
                    window.append(now)
                    return
                wait = window[0] + 60 - now
            if wait > max_wait:
                raise RateLimited(
                    f"MyInvois rate limit for {key.split('|')[-1]} reached on this Client ID.",
                    retry_after=wait,
                )
            self._sleep(wait)


class TokenCache:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._tokens: dict[tuple[str, str, str], tuple[str, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: tuple[str, str, str]) -> str | None:
        with self._lock:
            entry = self._tokens.get(key)
            if entry and entry[1] - TOKEN_REFRESH_MARGIN_SECONDS > self._clock():
                return entry[0]
            return None

    def put(self, key: tuple[str, str, str], token: str, expires_in: float) -> None:
        with self._lock:
            self._tokens[key] = (token, self._clock() + expires_in)

    def invalidate(self, key: tuple[str, str, str]) -> None:
        with self._lock:
            self._tokens.pop(key, None)


def _retry_after(response: httpx.Response) -> float | None:
    value = response.headers.get("Retry-After") or response.headers.get("X-Rate-Limit-Reset")
    if not value:
        return None
    try:
        return max(float(value), 0.0)
    except ValueError:
        try:
            return max(parsedate_to_datetime(value).timestamp() - time.time(), 0.0)
        except (TypeError, ValueError):
            return None


def _error_details(response: httpx.Response) -> dict[str, Any]:
    try:
        body = response.json()
    except ValueError:
        return {"status_code": response.status_code, "body": response.text[:500]}
    return {"status_code": response.status_code, "body": body}


class MyInvoisClient:
    def __init__(
        self,
        *,
        environment: str,
        api_base: str,
        http: httpx.Client | None = None,
        limiter: RateLimiter | None = None,
        tokens: TokenCache | None = None,
        max_rate_limit_wait: float = 5.0,
        sleep: Callable[[float], None] = time.sleep,
        timeout: float = 30.0,
    ) -> None:
        self.environment = environment
        self.api_base = api_base.rstrip("/")
        self.http = http or httpx.Client(timeout=timeout)
        self.limiter = limiter or RateLimiter()
        self.tokens = tokens or TokenCache()
        self.max_rate_limit_wait = max_rate_limit_wait
        self._sleep = sleep

    # -- auth -----------------------------------------------------------------------------------

    def _token_key(self, creds: ClientCredentials, on_behalf_of: str | None) -> tuple[str, str, str]:
        return (self.environment, creds.client_id, on_behalf_of or "")

    def access_token(self, creds: ClientCredentials, on_behalf_of: str | None) -> str:
        key = self._token_key(creds, on_behalf_of)
        cached = self.tokens.get(key)
        if cached:
            return cached
        self.limiter.acquire(
            f"{self.environment}|{creds.client_id}|login", RATE_LIMITS["login"], self.max_rate_limit_wait
        )
        headers = {"onbehalfof": on_behalf_of} if on_behalf_of else {}
        try:
            response = self.http.post(
                f"{self.api_base}/connect/token",
                headers=headers,
                data={
                    "client_id": creds.client_id,
                    "client_secret": creds.client_secret,
                    "grant_type": "client_credentials",
                    "scope": "InvoicingAPI",
                },
            )
        except httpx.HTTPError as exc:
            raise UpstreamError(f"MyInvois login failed: {exc}") from exc
        if response.status_code != 200:
            details = _error_details(response)
            details.pop("body", None)  # login errors can echo request fields; keep only the status
            raise UpstreamError(
                "MyInvois login was refused. Check the Client ID/secret and, for intermediaries, that the "
                "taxpayer has appointed you in the MyInvois portal.",
                status_code=response.status_code,
                details=details,
            )
        body = response.json()
        self.tokens.put(key, body["access_token"], float(body.get("expires_in", 3600)))
        return body["access_token"]

    # -- request plumbing -----------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        endpoint: str,
        creds: ClientCredentials,
        on_behalf_of: str | None,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> httpx.Response:
        key = self._token_key(creds, on_behalf_of)
        limit_key = f"{self.environment}|{creds.client_id}|{endpoint}"
        refreshed = retried_429 = False
        while True:
            self.limiter.acquire(limit_key, RATE_LIMITS[endpoint], self.max_rate_limit_wait)
            token = self.access_token(creds, on_behalf_of)
            try:
                response = self.http.request(
                    method,
                    f"{self.api_base}{path}",
                    params=params,
                    json=json,
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                )
            except httpx.HTTPError as exc:
                raise UpstreamError(f"MyInvois request failed: {exc}") from exc
            if response.status_code == 401 and not refreshed:
                self.tokens.invalidate(key)
                refreshed = True
                continue
            if response.status_code == 429:
                wait = _retry_after(response) or 60.0
                if not retried_429 and wait <= self.max_rate_limit_wait:
                    retried_429 = True
                    self._sleep(wait)
                    continue
                raise RateLimited(f"MyInvois throttled {endpoint}.", status_code=429, retry_after=wait)
            return response

    @staticmethod
    def _raise_for(response: httpx.Response, action: str) -> None:
        if response.status_code >= 400:
            raise UpstreamError(
                f"MyInvois {action} failed with HTTP {response.status_code}.",
                status_code=response.status_code,
                details=_error_details(response),
            )

    # -- endpoints ------------------------------------------------------------------------------

    def validate_tin(
        self, creds: ClientCredentials, on_behalf_of: str | None, *, tin: str, id_type: str, id_value: str
    ) -> bool:
        response = self._request(
            "GET",
            f"/api/v1.0/taxpayer/validate/{tin}",
            endpoint="validate_tin",
            creds=creds,
            on_behalf_of=on_behalf_of,
            params={"idType": id_type, "idValue": id_value},
        )
        if response.status_code == 200:
            return True
        if response.status_code in (400, 404):
            return False
        self._raise_for(response, "TIN validation")
        return False

    def search_tin(
        self,
        creds: ClientCredentials,
        on_behalf_of: str | None,
        *,
        id_type: str | None = None,
        id_value: str | None = None,
        taxpayer_name: str | None = None,
    ) -> str | None:
        params = {
            k: val for k, val in {"idType": id_type, "idValue": id_value, "taxpayerName": taxpayer_name}.items() if val
        }
        response = self._request(
            "GET",
            "/api/v1.0/taxpayer/search/tin",
            endpoint="search_tin",
            creds=creds,
            on_behalf_of=on_behalf_of,
            params=params,
        )
        if response.status_code == 404:
            return None
        self._raise_for(response, "TIN search")
        return response.json().get("tin")

    def submit(
        self, creds: ClientCredentials, on_behalf_of: str | None, documents: list[dict[str, str]]
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/api/v1.0/documentsubmissions/",
            endpoint="submit",
            creds=creds,
            on_behalf_of=on_behalf_of,
            json={"documents": documents},
        )
        self._raise_for(response, "submission")
        return response.json()

    def get_submission(
        self,
        creds: ClientCredentials,
        on_behalf_of: str | None,
        submission_uid: str,
        *,
        page_no: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/api/v1.0/documentsubmissions/{submission_uid}",
            endpoint="get_submission",
            creds=creds,
            on_behalf_of=on_behalf_of,
            params={"pageNo": page_no, "pageSize": page_size},
        )
        self._raise_for(response, "get submission")
        return response.json()

    def document_details(self, creds: ClientCredentials, on_behalf_of: str | None, uuid: str) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/api/v1.0/documents/{uuid}/details",
            endpoint="document_details",
            creds=creds,
            on_behalf_of=on_behalf_of,
        )
        self._raise_for(response, "get document details")
        return response.json()

    def _change_state(
        self, creds: ClientCredentials, on_behalf_of: str | None, uuid: str, *, status: str, reason: str, endpoint: str
    ) -> dict[str, Any]:
        response = self._request(
            "PUT",
            f"/api/v1.0/documents/state/{uuid}/state",
            endpoint=endpoint,
            creds=creds,
            on_behalf_of=on_behalf_of,
            json={"status": status, "reason": reason},
        )
        self._raise_for(response, status)
        return response.json() if response.content else {}

    def cancel(self, creds: ClientCredentials, on_behalf_of: str | None, uuid: str, reason: str) -> dict[str, Any]:
        return self._change_state(creds, on_behalf_of, uuid, status="cancelled", reason=reason, endpoint="cancel")

    def reject(self, creds: ClientCredentials, on_behalf_of: str | None, uuid: str, reason: str) -> dict[str, Any]:
        return self._change_state(creds, on_behalf_of, uuid, status="rejected", reason=reason, endpoint="reject")
