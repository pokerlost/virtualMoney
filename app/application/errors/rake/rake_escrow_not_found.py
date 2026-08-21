"""RakeEscrowNotFound application error."""

from __future__ import annotations

from application.errors.base import NotFoundError


class RakeEscrowNotFound(NotFoundError):
    """No table escrow exists for the table and asset."""

    error_code = "RAKE_ESCROW_NOT_FOUND"
    public_message = "The table escrow account for the rake charge was not found."
