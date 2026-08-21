"""Account lookup use case."""

from __future__ import annotations

from application.errors import AccountNotFound
from persistence.database.models import AccountModel
from persistence.repositories import SQLAlchemyAccountRepository

from .query import GetAccountQuery


class GetAccountHandler:
    """Load an account by its stable UUID."""

    def __init__(self, accounts: SQLAlchemyAccountRepository) -> None:
        """Store request-scoped collaborators."""
        self._accounts = accounts

    async def execute(self, query: GetAccountQuery) -> AccountModel:
        """Return the account or report not found."""
        account = await self._accounts.get_by_id(query.account_id)
        if account is None:
            raise AccountNotFound()
        return account
