"""LedgerAccountNotFound application error."""

from __future__ import annotations

from application.errors.base import InvalidOperationError


class LedgerAccountNotFound(InvalidOperationError):
    """At least one posting account does not exist."""

    error_code = "LEDGER_ACCOUNT_NOT_FOUND"
    public_message = "One or more posting accounts were not found."
