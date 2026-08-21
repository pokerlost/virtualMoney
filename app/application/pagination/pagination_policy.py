"""Runtime pagination limit policy."""

from __future__ import annotations

from application.errors import HistoryPaginationInvalid

from .pagination_input import PaginationInput


class PaginationPolicy:
    """Resolve optional limits against validated runtime settings."""

    __slots__ = ("_default_limit", "_maximum_limit")

    def __init__(self, default_limit: int, maximum_limit: int) -> None:
        """Store validated default and maximum page sizes."""
        self._default_limit = default_limit
        self._maximum_limit = maximum_limit

    def resolve_limit(self, pagination: PaginationInput) -> int:
        """Return an effective limit or reject a configured-policy violation."""
        limit = pagination.limit or self._default_limit
        if limit > self._maximum_limit:
            raise HistoryPaginationInvalid()
        return limit
