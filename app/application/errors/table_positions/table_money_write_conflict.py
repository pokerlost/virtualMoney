"""TableMoneyWriteConflict application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class TableMoneyWriteConflict(ConflictError):
    """A concurrent table-money write cannot resolve as a replay."""

    error_code = "TABLE_MONEY_WRITE_CONFLICT"
    public_message = "A concurrent table-money operation conflict occurred."
