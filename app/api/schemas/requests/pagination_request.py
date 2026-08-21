"""Shared pagination request body component."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.pagination import CURSOR_MAX_LENGTH, PaginationInput, PaginationLimit


class PaginationRequest(RequestModel):
    """Accept an opaque keyset cursor and optional page size."""

    cursor: str | None = Field(
        default=None,
        max_length=CURSOR_MAX_LENGTH,
        description="Opaque cursor returned by the previous page.",
    )
    limit: PaginationLimit | None = Field(
        default=None,
        description="Requested number of immutable rows within the configured maximum.",
    )

    def to_application(self) -> PaginationInput:
        """Map transport fields to the application pagination input."""
        return PaginationInput(cursor=self.cursor, limit=self.limit)
