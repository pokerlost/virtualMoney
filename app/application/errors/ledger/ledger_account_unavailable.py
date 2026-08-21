"""LedgerAccountUnavailable application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class LedgerAccountUnavailable(ConflictError):
    """An account state prohibits the ledger operation."""

    error_code = "LEDGER_ACCOUNT_UNAVAILABLE"
    public_message = "One or more account states prohibit this operation."
