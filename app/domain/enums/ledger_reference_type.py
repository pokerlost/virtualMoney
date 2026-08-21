"""Platform-owned ledger reference namespaces."""

from __future__ import annotations

from enum import StrEnum


class LedgerReferenceType(StrEnum):
    """Identify internal business records linked from immutable ledger transactions."""

    HOLD = "HOLD"
    TABLE_POSITION = "TABLE_POSITION"
    POKER_HAND = "POKER_HAND"
    FINANCIAL_REFUND = "FINANCIAL_REFUND"
