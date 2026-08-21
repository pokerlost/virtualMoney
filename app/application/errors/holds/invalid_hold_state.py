"""InvalidHoldState application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class InvalidHoldState(ConflictError):
    """The hold state does not allow the transition."""

    error_code = "INVALID_HOLD_STATE"
    public_message = "The current hold state does not allow this operation."
