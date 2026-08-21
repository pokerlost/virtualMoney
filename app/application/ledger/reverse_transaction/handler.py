"""Ledger reversal use case."""

from __future__ import annotations

import logfire

from application.ledger.services import LedgerReversal
from persistence.database.models import LedgerTransactionModel

from .command import ReverseLedgerTransactionCommand


class ReverseTransactionHandler:
    """Execute one full immutable ledger reversal."""

    def __init__(self, reversal: LedgerReversal) -> None:
        """Store request-scoped collaborators."""
        self._reversal = reversal

    async def execute(self, command: ReverseLedgerTransactionCommand) -> LedgerTransactionModel:
        """Return a new reversal or its exact replay."""
        result = await self._reversal.reverse(command)
        transaction = result.transaction
        logfire.info(
            "Ledger transaction reversal resolved",
            idempotent_replay=result.idempotent_replay,
            ledger_transaction_id=str(transaction.id),
            operation_id=str(transaction.operation_id),
        )
        return transaction
