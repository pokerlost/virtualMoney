"""Ledger transaction lookup use case."""

from __future__ import annotations

from application.errors import LedgerTransactionNotFound
from persistence.database.models import LedgerTransactionModel
from persistence.repositories import SQLAlchemyLedgerRepository

from .query import GetTransactionQuery


class GetTransactionHandler:
    """Load an immutable ledger transaction with its entries."""

    def __init__(self, ledger: SQLAlchemyLedgerRepository) -> None:
        """Store request-scoped collaborators."""
        self._ledger = ledger

    async def execute(self, query: GetTransactionQuery) -> LedgerTransactionModel:
        """Return the transaction or report not found."""
        transaction = await self._ledger.get_by_id_with_entries(query.transaction_id)
        if transaction is None:
            raise LedgerTransactionNotFound()
        return transaction
