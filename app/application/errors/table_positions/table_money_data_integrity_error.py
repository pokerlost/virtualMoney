"""TableMoneyDataIntegrityError application error."""

from __future__ import annotations

from application.errors.base import IntegrityError


class TableMoneyDataIntegrityError(IntegrityError):
    """Table-position audit and linked records are inconsistent."""

    error_code = "TABLE_MONEY_DATA_INTEGRITY_ERROR"
    public_message = "The table-money lifecycle data has an internal error."
