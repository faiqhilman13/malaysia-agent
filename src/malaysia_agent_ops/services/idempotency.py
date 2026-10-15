"""Idempotency keys: a retried write with the same key returns the first result instead of acting twice."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import IdempotencyRecord
from ..errors import Conflict


def request_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def run_once(
    session: Session,
    *,
    tenant_id: str,
    scope: str,
    key: str | None,
    payload: Any,
    fn: Callable[[], dict[str, Any]],
    replay_if: Callable[[dict[str, Any]], bool] = lambda result: True,
) -> dict[str, Any]:
    """Run `fn` at most once per (tenant, scope, key).

    `replay_if` decides whether a stored result is final. Results that only report a waiting state
    (e.g. awaiting approval) are not stored, so a retry after approval runs again.
    """
    if not key:
        return fn()
    digest = request_hash(payload)
    existing = session.scalar(
        select(IdempotencyRecord).where(
            IdempotencyRecord.tenant_id == tenant_id,
            IdempotencyRecord.scope == scope,
            IdempotencyRecord.key == key,
        )
    )
    if existing is not None:
        if existing.request_hash != digest:
            raise Conflict("This idempotency key was already used with a different request.")
        if existing.response is not None:
            return {**existing.response, "idempotent_replay": True}
    result = fn()
    if not replay_if(result):
        return result
    if existing is not None:
        existing.response = result
        return result
    try:
        with session.begin_nested():
            session.add(
                IdempotencyRecord(tenant_id=tenant_id, scope=scope, key=key, request_hash=digest, response=result)
            )
    except IntegrityError as exc:
        raise Conflict("A concurrent request with this idempotency key is in progress.") from exc
    return result
