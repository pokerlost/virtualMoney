"""Asset lookup by canonical code."""

from __future__ import annotations

from application.errors import AssetNotFound
from persistence.database.models import AssetModel
from persistence.repositories import SQLAlchemyAssetRepository

from .query import GetAssetByCodeQuery


class GetAssetByCodeHandler:
    """Load an internal asset by its canonical code."""

    def __init__(self, assets: SQLAlchemyAssetRepository) -> None:
        """Store request-scoped collaborators."""
        self._assets = assets

    async def execute(self, query: GetAssetByCodeQuery) -> AssetModel:
        """Return the asset or report not found."""
        asset = await self._assets.get_by_code(query.code)
        if asset is None:
            raise AssetNotFound()
        return asset
