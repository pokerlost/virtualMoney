"""HistoryPaginationInvalid application error."""

from __future__ import annotations

from application.errors.base import InvalidOperationError


class HistoryPaginationInvalid(InvalidOperationError):
    """A page limit exceeds the configured policy."""

    error_code = "HISTORY_PAGINATION_INVALID"
    public_message = "The financial history pagination request is invalid."
