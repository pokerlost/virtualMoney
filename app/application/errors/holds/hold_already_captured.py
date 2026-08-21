"""HoldAlreadyCaptured application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class HoldAlreadyCaptured(ConflictError):
    """A new operation targets an already captured hold."""

    error_code = "HOLD_ALREADY_CAPTURED"
    public_message = "The funds hold has already been fully captured."
