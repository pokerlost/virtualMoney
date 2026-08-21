"""TableEscrowUnavailable application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class TableEscrowUnavailable(ConflictError):
    """The table escrow cannot accept the operation."""

    error_code = "TABLE_ESCROW_UNAVAILABLE"
    public_message = "The table escrow account is unavailable for this operation."
