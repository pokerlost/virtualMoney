"""Public asset entity schema."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import ORMSchema
from domain.enums import AssetStatus
from domain.types import AssetCode, NonNilUUID, UtcDatetime


class AssetSchema(ORMSchema):
    """Expose internal asset metadata without balances."""

    id: NonNilUUID = Field(description="Stable service-owned asset UUID.")
    code: AssetCode = Field(description="Canonical uppercase asset code.")
    name: str = Field(min_length=1, max_length=128, description="Display name.")
    minor_unit_scale: int = Field(
        strict=True,
        ge=0,
        le=8,
        description="Decimal places used only to display integer minimal units.",
    )
    status: AssetStatus = Field(description="Availability for future operations.")
    created_at: UtcDatetime = Field(description="Creation timestamp in UTC.")
    updated_at: UtcDatetime = Field(description="Last metadata update timestamp in UTC.")
