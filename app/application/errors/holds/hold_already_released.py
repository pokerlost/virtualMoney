"""HoldAlreadyReleased application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class HoldAlreadyReleased(ConflictError):
    """A new operation targets an already released hold."""

    error_code = "HOLD_ALREADY_RELEASED"
    public_message = "The funds hold has already been fully released."
