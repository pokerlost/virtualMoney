"""RakeDataIntegrityError application error."""

from __future__ import annotations

from application.errors.base import IntegrityError


class RakeDataIntegrityError(IntegrityError):
    """Rake audit and linked financial data are inconsistent."""

    error_code = "RAKE_DATA_INTEGRITY_ERROR"
    public_message = "The rake operation data has an internal error."
