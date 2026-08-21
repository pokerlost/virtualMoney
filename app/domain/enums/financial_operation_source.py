"""Immutable financial operation audit sources."""

from __future__ import annotations

from enum import StrEnum


class FinancialOperationSource(StrEnum):
    """Identify the authoritative audit source for an operation."""

    LEDGER = "LEDGER"
    HOLD = "HOLD"
    TABLE_MONEY = "TABLE_MONEY"
    RAKE = "RAKE"
    REFUND = "REFUND"
