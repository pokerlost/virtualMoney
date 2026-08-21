"""HoldNotFound application error."""

from __future__ import annotations

from application.errors.base import NotFoundError


class HoldNotFound(NotFoundError):
    """The requested hold does not exist."""

    error_code = "HOLD_NOT_FOUND"
    public_message = "The funds hold was not found."
