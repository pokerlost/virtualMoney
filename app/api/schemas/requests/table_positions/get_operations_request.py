"""Table-position operation history request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from api.schemas.requests.pagination_request import PaginationRequest
from application.table_positions import GetOperationsQuery
from domain.types import NonNilUUID


class GetOperationsRequest(RequestModel):
    """Identify a position and one bounded audit page."""

    position_id: NonNilUUID = Field(description="Stable service-owned position UUID.")
    pagination: PaginationRequest = Field(
        default_factory=PaginationRequest,
        description="Cursor pagination input.",
    )

    def to_query(self) -> GetOperationsQuery:
        """Map validated transport fields to the operation-history query."""
        return GetOperationsQuery(
            position_id=self.position_id,
            pagination=self.pagination.to_application(),
        )
