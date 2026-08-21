"""Financial account lifecycle states."""

from __future__ import annotations

from enum import StrEnum


class AccountStatus(StrEnum):
    """Control whether an account accepts new financial operations."""

    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"
