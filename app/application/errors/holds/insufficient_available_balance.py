"""InsufficientAvailableBalance application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class InsufficientAvailableBalance(ConflictError):
    """The USER account lacks enough available funds."""

    error_code = "INSUFFICIENT_AVAILABLE_BALANCE"
    public_message = "There are insufficient available funds for the hold."
