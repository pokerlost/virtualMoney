"""AccountBalanceMissing application error."""

from __future__ import annotations

from application.errors.base import IntegrityError


class AccountBalanceMissing(IntegrityError):
    """An account exists without its required balance projection."""

    error_code = "ACCOUNT_BALANCE_MISSING"
    public_message = "The account balance projection is unavailable due to an internal error."
