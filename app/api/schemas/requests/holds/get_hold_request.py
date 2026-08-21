"""Hold lookup request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.holds import GetHoldQuery
from domain.types import NonNilUUID


class GetHoldRequest(RequestModel):
    """Identify one funds hold."""

    hold_id: NonNilUUID = Field(description="Stable service-owned hold UUID.")

    def to_query(self) -> GetHoldQuery:
        """Map validated transport fields to the application query."""
        return GetHoldQuery(hold_id=self.hold_id)
