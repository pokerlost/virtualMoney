"""AccountCreationConflict application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class AccountCreationConflict(ConflictError):
    """An account identity is associated with other metadata."""

    error_code = "ACCOUNT_CREATION_CONFLICT"
    public_message = "The financial account already exists with different data."
