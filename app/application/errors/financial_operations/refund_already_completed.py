"""RefundAlreadyCompleted application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class RefundAlreadyCompleted(ConflictError):
    """The target already has a full compensation."""

    error_code = "REFUND_ALREADY_COMPLETED"
    public_message = "The financial operation has already been fully compensated."
