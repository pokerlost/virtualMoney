"""RefundDataIntegrityError application error."""

from __future__ import annotations

from application.errors.base import IntegrityError


class RefundDataIntegrityError(IntegrityError):
    """Refund audit and linked reversal data are inconsistent."""

    error_code = "REFUND_DATA_INTEGRITY_ERROR"
    public_message = "The financial compensation data has an internal error."
