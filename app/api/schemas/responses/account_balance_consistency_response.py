"""Public balance reconciliation response."""

from __future__ import annotations

from api.schemas.base import ResponseModel
from domain.types import NonNegativeMoneyMinor, NonNilUUID, SignedMoneyMinor


class AccountBalanceConsistencyResponse(ResponseModel):
    """Expose mismatches without repairing authoritative state."""

    account_id: NonNilUUID
    projected_posted_balance_minor: SignedMoneyMinor
    ledger_posted_balance_minor: SignedMoneyMinor
    projected_held_balance_minor: NonNegativeMoneyMinor
    active_holds_balance_minor: NonNegativeMoneyMinor
    posted_is_consistent: bool
    held_is_consistent: bool
    is_consistent: bool
