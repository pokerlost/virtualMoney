"""Asset UUID lookup request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.assets import GetAssetQuery
from domain.types import NonNilUUID


class GetAssetRequest(RequestModel):
    """Identify one internal asset by UUID."""

    asset_id: NonNilUUID = Field(description="Stable service-owned asset UUID.")

    def to_query(self) -> GetAssetQuery:
        """Map validated transport fields to the application query."""
        return GetAssetQuery(asset_id=self.asset_id)
