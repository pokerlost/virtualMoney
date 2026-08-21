"""RakeWriteConflict application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class RakeWriteConflict(ConflictError):
    """A concurrent rake write cannot resolve as a replay."""

    error_code = "RAKE_WRITE_CONFLICT"
    public_message = "A concurrent rake charge conflict occurred."
