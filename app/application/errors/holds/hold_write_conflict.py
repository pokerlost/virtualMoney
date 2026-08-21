"""HoldWriteConflict application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class HoldWriteConflict(ConflictError):
    """A concurrent hold write cannot resolve as a replay."""

    error_code = "HOLD_WRITE_CONFLICT"
    public_message = "A concurrent hold update conflict occurred."
