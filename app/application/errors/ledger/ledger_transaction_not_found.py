"""LedgerTransactionNotFound application error."""

from __future__ import annotations

from application.errors.base import NotFoundError


class LedgerTransactionNotFound(NotFoundError):
    """The requested ledger transaction does not exist."""

    error_code = "LEDGER_TRANSACTION_NOT_FOUND"
    public_message = "The ledger transaction was not found."
