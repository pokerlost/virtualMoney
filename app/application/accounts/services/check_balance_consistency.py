"""Read-only account balance reconciliation use case."""

from __future__ import annotations

from uuid import UUID

import logfire

from application.accounts.get_balance import GetAccountBalanceHandler, GetAccountBalanceQuery
from persistence.repositories import SQLAlchemyHoldRepository, SQLAlchemyLedgerRepository

from .account_balance_consistency import AccountBalanceConsistency


class CheckAccountBalanceConsistency:
    """Compare a projection with authoritative immutable sources."""

    def __init__(
        self,
        get_balance: GetAccountBalanceHandler,
        ledger: SQLAlchemyLedgerRepository,
        holds: SQLAlchemyHoldRepository,
    ) -> None:
        """Store request-scoped collaborators."""
        self._get_balance = get_balance
        self._ledger = ledger
        self._holds = holds

    async def execute(self, account_id: UUID) -> AccountBalanceConsistency:
        """Report projection mismatches without changing financial data."""
        details = await self._get_balance.execute(GetAccountBalanceQuery(account_id=account_id))
        ledger_balance = await self._ledger.calculate_posted_balance_from_ledger(account_id)
        active_holds = await self._holds.calculate_active_held_balance(account_id)
        posted_matches = details.posted_balance_minor == ledger_balance
        held_matches = details.held_balance_minor == active_holds
        result = AccountBalanceConsistency(
            account_id=account_id,
            projected_posted_balance_minor=details.posted_balance_minor,
            ledger_posted_balance_minor=ledger_balance,
            projected_held_balance_minor=details.held_balance_minor,
            active_holds_balance_minor=active_holds,
            posted_is_consistent=posted_matches,
            held_is_consistent=held_matches,
            is_consistent=posted_matches and held_matches,
        )
        if not result.is_consistent:
            logfire.error(
                "Financial projection reconciliation found a mismatch",
                account_id=str(account_id),
                posted_is_consistent=posted_matches,
                held_is_consistent=held_matches,
            )
        return result
