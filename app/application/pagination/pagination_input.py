"""Validated pagination input shared by history queries."""

from __future__ import annotations

from typing import Final

from pydantic import Field

from domain import ValueModel

from .pagination_limit import PaginationLimit

CURSOR_MAX_LENGTH: Final[int] = 256


class PaginationInput(ValueModel):
    """Opaque continuation cursor and optional requested page size."""

    cursor: str | None = Field(default=None, max_length=CURSOR_MAX_LENGTH)
    limit: PaginationLimit | None = None
