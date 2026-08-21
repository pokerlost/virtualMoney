"""Public history application errors."""

from __future__ import annotations

from .history_cursor_invalid import HistoryCursorInvalid
from .history_pagination_invalid import HistoryPaginationInvalid

__all__ = (
    "HistoryCursorInvalid",
    "HistoryPaginationInvalid",
)
