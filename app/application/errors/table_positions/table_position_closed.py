"""TablePositionClosed application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class TablePositionClosed(ConflictError):
    """A mutation targets a terminal CLOSED position."""

    error_code = "TABLE_POSITION_CLOSED"
    public_message = "The player's financial table position is already closed."
