"""AccountBalanceOverflow application error."""

from __future__ import annotations

from application.errors.base import InvalidOperationError


class AccountBalanceOverflow(InvalidOperationError):
    """A projected balance or revision exceeds BIGINT bounds."""

    error_code = "ACCOUNT_BALANCE_OVERFLOW"
    public_message = "The financial result is outside the supported integer range."
