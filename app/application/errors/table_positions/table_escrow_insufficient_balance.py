"""TableEscrowInsufficientBalance application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class TableEscrowInsufficientBalance(ConflictError):
    """Pooled table escrow cannot cover the final stack."""

    error_code = "TABLE_ESCROW_INSUFFICIENT_BALANCE"
    public_message = "The table escrow account has insufficient funds for the payout."
