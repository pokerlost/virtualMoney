"""Asset code lookup request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.assets import GetAssetByCodeQuery
from domain.types import AssetCode


class GetAssetByCodeRequest(RequestModel):
    """Identify one internal asset by canonical code."""

    code: AssetCode = Field(
        description="Two to sixteen characters normalized to canonical uppercase.",
    )

    def to_query(self) -> GetAssetByCodeQuery:
        """Map validated transport fields to the application query."""
        return GetAssetByCodeQuery(code=self.code)
