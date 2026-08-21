"""HoldDataIntegrityError application error."""

from __future__ import annotations

from application.errors.base import IntegrityError


class HoldDataIntegrityError(IntegrityError):
    """Hold audit and lifecycle state are inconsistent."""

    error_code = "HOLD_DATA_INTEGRITY_ERROR"
    public_message = "The hold data is unavailable due to an internal error."
