"""SQLAlchemy asset repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from persistence.database.models import AssetModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyAssetRepository(SQLAlchemyEntityRepository[AssetModel]):
    """Read assets through one injected request session."""

    model = AssetModel

    async def get_by_code(self, code: str) -> AssetModel | None:
        """Return one asset by its canonical code."""
        result = await self._read_scalar(
            select(AssetModel).where(AssetModel.code == code),
        )
        model = result.one_or_none()
        return model

    async def get_by_id_for_update(self, asset_id: UUID) -> AssetModel | None:
        """Lock one asset row for dependent account provisioning."""
        result = await self._read_scalar(
            select(AssetModel).where(AssetModel.id == asset_id).with_for_update(),
        )
        return result.one_or_none()
