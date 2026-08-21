"""ReBuyHoldInvalid application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class ReBuyHoldInvalid(ConflictError):
    """A hold does not match the existing OPEN position."""

    error_code = "REBUY_HOLD_INVALID"
    public_message = "The specified hold is not valid for this ReBuy."
