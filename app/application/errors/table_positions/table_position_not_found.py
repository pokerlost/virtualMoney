"""TablePositionNotFound application error."""

from __future__ import annotations

from application.errors.base import NotFoundError


class TablePositionNotFound(NotFoundError):
    """The requested durable position does not exist."""

    error_code = "TABLE_POSITION_NOT_FOUND"
    public_message = "The player's financial table position was not found."
