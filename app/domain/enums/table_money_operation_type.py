"""High-level table money operation types."""

from __future__ import annotations

from enum import StrEnum


class TableMoneyOperationType(StrEnum):
    """Classify transfers involving a player table position."""

    BUY_IN = "BUY_IN"
    REBUY = "REBUY"
    CASH_OUT = "CASH_OUT"
