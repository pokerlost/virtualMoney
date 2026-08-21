"""Bounded application pagination result."""

from __future__ import annotations

from domain import ValueModel


class PaginationPage[ItemT](ValueModel):
    """One keyset page and an optional continuation cursor."""

    items: list[ItemT]
    next_cursor: str | None = None
