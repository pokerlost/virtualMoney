"""LedgerDataIntegrityError application error."""

from __future__ import annotations

from application.errors.base import IntegrityError


class LedgerDataIntegrityError(IntegrityError):
    """A persisted ledger write cannot be read back in the same transaction."""

    error_code = "LEDGER_DATA_INTEGRITY_ERROR"
    public_message = "Ledger data integrity could not be verified."
