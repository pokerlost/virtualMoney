"""RakeInsufficientEscrow application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class RakeInsufficientEscrow(ConflictError):
    """Table escrow cannot cover the rake amount."""

    error_code = "RAKE_INSUFFICIENT_ESCROW"
    public_message = "The table escrow account has insufficient funds for rake."
