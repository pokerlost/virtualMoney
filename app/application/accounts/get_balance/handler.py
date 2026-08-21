"""Account balance lookup use case."""

from __future__ import annotations

from application.errors import AccountBalanceMissing, AccountNotFound
from persistence.repositories import (
    SQLAlchemyAccountBalanceRepository,
    SQLAlchemyAccountRepository,
)

from .query import GetAccountBalanceQuery
from .result import AccountBalanceDetails


class GetAccountBalanceHandler:
    """Read a materialized balance without runtime aggregate queries."""

    def __init__(
        self,
        accounts: SQLAlchemyAccountRepository,
        balances: SQLAlchemyAccountBalanceRepository,
    ) -> None:
        """Store request-scoped collaborators."""
        self._accounts = accounts
        self._balances = balances

    async def execute(self, query: GetAccountBalanceQuery) -> AccountBalanceDetails:
        """Return posted, held, available, and asset information."""
        account = await self._accounts.get_by_id(query.account_id)
        if account is None:
            raise AccountNotFound()
        balance = await self._balances.get_by_account_id(query.account_id)
        if balance is None:
            raise AccountBalanceMissing()
        return AccountBalanceDetails(
            account_id=account.id,
            asset_id=account.asset_id,
            posted_balance_minor=balance.posted_balance_minor,
            held_balance_minor=balance.held_balance_minor,
            available_balance_minor=(balance.posted_balance_minor - balance.held_balance_minor),
            version=balance.version,
            updated_at=balance.updated_at,
        )
