"""HoldAccountUnavailable application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class HoldAccountUnavailable(ConflictError):
    """An account type or state prohibits the hold operation."""

    error_code = "HOLD_ACCOUNT_UNAVAILABLE"
    public_message = "The account state or type prohibits this hold operation."
