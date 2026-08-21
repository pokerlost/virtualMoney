"""Immutable ledger transaction classifications."""

from __future__ import annotations

from enum import StrEnum


class LedgerTransactionType(StrEnum):
    """Classify implemented low-level ledger operations."""

    ADJUSTMENT = "ADJUSTMENT"
    CASH_OUT = "CASH_OUT"
    HOLD_CAPTURE = "HOLD_CAPTURE"
    RAKE = "RAKE"
    REVERSAL = "REVERSAL"
