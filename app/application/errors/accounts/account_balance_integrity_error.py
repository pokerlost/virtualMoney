"""AccountBalanceIntegrityError application error."""

from __future__ import annotations

from application.errors.base import IntegrityError


class AccountBalanceIntegrityError(IntegrityError):
    """A persisted balance projection violates financial invariants."""

    error_code = "ACCOUNT_BALANCE_INTEGRITY_ERROR"
    public_message = "The account balance projection has an inconsistent internal state."
