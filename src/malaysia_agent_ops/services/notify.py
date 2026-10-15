"""Delivers approval links to approvers on their own channels, outside the agent's reach.

The link carries a one-time token. It is sent to the approver directly and never returned through
MCP or REST, so an agent cannot approve its own request.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol

log = logging.getLogger("myops.notify")


@dataclass(frozen=True)
class ApprovalMessage:
    user_id: str
    email: str
    phone: str | None
    subject: str
    body: str
    link: str


class Notifier(Protocol):
    def send(self, message: ApprovalMessage) -> None: ...


class LogNotifier:
    """Development only: writes the link to the server log. Do not use where logs are shared."""

    def send(self, message: ApprovalMessage) -> None:
        log.warning("Approval link for %s: %s\n%s", message.email, message.link, message.body)


@dataclass
class MemoryNotifier:
    """For tests."""

    sent: list[ApprovalMessage] = field(default_factory=list)

    def send(self, message: ApprovalMessage) -> None:
        self.sent.append(message)
