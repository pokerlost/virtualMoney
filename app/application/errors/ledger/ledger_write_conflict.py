"""LedgerWriteConflict application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class LedgerWriteConflict(ConflictError):
    """A concurrent ledger write cannot resolve as a replay."""

    error_code = "LEDGER_WRITE_CONFLICT"
    public_message = "A concurrent ledger posting conflict occurred."
