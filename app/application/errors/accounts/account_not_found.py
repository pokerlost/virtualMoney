"""AccountNotFound application error."""

from __future__ import annotations

from application.errors.base import NotFoundError


class AccountNotFound(NotFoundError):
    """The requested account does not exist."""

    error_code = "ACCOUNT_NOT_FOUND"
    public_message = "The financial account was not found."
