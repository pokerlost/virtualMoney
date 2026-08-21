"""Immutable ledger transaction states."""

from __future__ import annotations

from enum import StrEnum


class LedgerTransactionStatus(StrEnum):
    """Represent the single supported immutable ledger state."""

    POSTED = "POSTED"
