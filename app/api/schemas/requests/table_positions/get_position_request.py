"""Table-position lookup request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.table_positions import GetPositionQuery
from domain.types import NonNilUUID


class GetPositionRequest(RequestModel):
    """Identify one durable financial table position."""

    position_id: NonNilUUID = Field(description="Stable service-owned position UUID.")

    def to_query(self) -> GetPositionQuery:
        """Map validated transport fields to the application query."""
        return GetPositionQuery(position_id=self.position_id)
