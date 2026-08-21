"""Asset feature composition."""

from __future__ import annotations

from api.dependencies import DatabaseSession
from application.assets import GetAssetByCodeHandler, GetAssetHandler
from persistence.repositories import SQLAlchemyAssetRepository


def provide_get_asset(session: DatabaseSession) -> GetAssetHandler:
    """Compose asset lookup by UUID."""
    return GetAssetHandler(SQLAlchemyAssetRepository(session))


def provide_get_asset_by_code(session: DatabaseSession) -> GetAssetByCodeHandler:
    """Compose asset lookup by canonical code."""
    return GetAssetByCodeHandler(SQLAlchemyAssetRepository(session))
