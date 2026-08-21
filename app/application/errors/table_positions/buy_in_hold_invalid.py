"""BuyInHoldInvalid application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class BuyInHoldInvalid(ConflictError):
    """A hold or source account cannot fund the initial BuyIn."""

    error_code = "BUY_IN_HOLD_INVALID"
    public_message = "The specified hold is not valid for the initial BuyIn."
