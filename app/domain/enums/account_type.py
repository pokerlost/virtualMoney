"""Financial account purposes."""

from __future__ import annotations

from enum import StrEnum


class AccountType(StrEnum):
    """Describe the unambiguous purpose of an account."""

    USER = "USER"
    TREASURY = "TREASURY"
    RAKE = "RAKE"
    TABLE_ESCROW = "TABLE_ESCROW"
