"""Asset lookup by UUID."""

from __future__ import annotations

from application.errors import AssetNotFound
from persistence.database.models import AssetModel
from persistence.repositories import SQLAlchemyAssetRepository

from .query import GetAssetQuery


class GetAssetHandler:
    """Load an internal asset by stable UUID."""

    def __init__(self, assets: SQLAlchemyAssetRepository) -> None:
        """Store request-scoped collaborators."""
        self._assets = assets

    async def execute(self, query: GetAssetQuery) -> AssetModel:
        """Return the asset or report not found."""
        asset = await self._assets.get_by_id(query.asset_id)
        if asset is None:
            raise AssetNotFound()
        return asset
