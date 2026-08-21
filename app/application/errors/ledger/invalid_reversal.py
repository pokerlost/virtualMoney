"""InvalidReversal application error."""

from __future__ import annotations

from application.errors.base import InvalidOperationError


class InvalidReversal(InvalidOperationError):
    """The target transaction cannot be fully reversed."""

    error_code = "INVALID_LEDGER_REVERSAL"
    public_message = "The specified ledger transaction cannot be reversed."
