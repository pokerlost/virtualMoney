"""Generic cursor pagination response."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import ResponseModel


class PaginationResponse[T](ResponseModel):
    """Expose one bounded keyset page."""

    items: list[T]
    next_cursor: str | None = Field(
        default=None,
        description="Opaque cursor for the next page, or null at the end.",
    )
