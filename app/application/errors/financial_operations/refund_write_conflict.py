"""RefundWriteConflict application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class RefundWriteConflict(ConflictError):
    """A concurrent refund write cannot resolve as a replay."""

    error_code = "REFUND_WRITE_CONFLICT"
    public_message = "A concurrent financial compensation conflict occurred."
