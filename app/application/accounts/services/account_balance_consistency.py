"""Read-only account balance reconciliation result."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNegativeMoneyMinor, NonNilUUID, SignedMoneyMinor


class AccountBalanceConsistency(ValueModel):
    """Comparison of a projection with ledger and ACTIVE holds."""

    account_id: NonNilUUID
    projected_posted_balance_minor: SignedMoneyMinor
    ledger_posted_balance_minor: SignedMoneyMinor
    projected_held_balance_minor: NonNegativeMoneyMinor
    active_holds_balance_minor: NonNegativeMoneyMinor
    posted_is_consistent: bool
    held_is_consistent: bool
    is_consistent: bool
