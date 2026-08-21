"""PositionOwnershipMismatch application error."""

from __future__ import annotations

from application.errors.base import InvalidOperationError


class PositionOwnershipMismatch(InvalidOperationError):
    """The USER account owner does not match the player."""

    error_code = "POSITION_OWNERSHIP_MISMATCH"
    public_message = "The financial account owner does not match the position player."
