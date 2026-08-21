"""LedgerTransactionAlreadyReversed application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class LedgerTransactionAlreadyReversed(ConflictError):
    """The original transaction already has a full reversal."""

    error_code = "LEDGER_TRANSACTION_ALREADY_REVERSED"
    public_message = "The ledger transaction has already been fully reversed."
