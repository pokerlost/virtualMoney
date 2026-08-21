"""Balance projection delta."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID, ReversibleMoneyMinor


class BalanceProjectionDelta(ValueModel):
    """Posted and held changes from one logical financial operation."""

    account_id: NonNilUUID
    posted_delta_minor: ReversibleMoneyMinor = 0
    held_delta_minor: ReversibleMoneyMinor = 0
