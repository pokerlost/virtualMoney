"""TablePositionAlreadyOpen application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class TablePositionAlreadyOpen(ConflictError):
    """A matching OPEN position already exists."""

    error_code = "TABLE_POSITION_ALREADY_OPEN"
    public_message = "The player already has an open financial position at this table."
