"""HistoryCursorInvalid application error."""

from __future__ import annotations

from application.errors.base import InvalidOperationError


class HistoryCursorInvalid(InvalidOperationError):
    """An opaque keyset cursor is invalid."""

    error_code = "HISTORY_CURSOR_INVALID"
    public_message = "The financial history cursor has an invalid format."
