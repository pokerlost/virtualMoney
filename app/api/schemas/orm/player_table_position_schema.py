"""Public durable table-position schema."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import ORMSchema
from domain.enums import PlayerTablePositionStatus
from domain.types import NonNegativeMoneyMinor, NonNilUUID, PositiveMoneyMinor, UtcDatetime


class PlayerTablePositionSchema(ORMSchema):
    """Expose the durable financial lifecycle, not a live poker stack."""

    id: NonNilUUID
    user_id: NonNilUUID
    table_id: NonNilUUID
    asset_id: NonNilUUID
    user_account_id: NonNilUUID
    table_escrow_account_id: NonNilUUID
    status: PlayerTablePositionStatus
    total_buy_in_minor: PositiveMoneyMinor
    total_cash_out_minor: NonNegativeMoneyMinor
    created_at: UtcDatetime
    updated_at: UtcDatetime
    closed_at: UtcDatetime | None = Field(
        description="Terminal CashOut timestamp, or null while OPEN.",
    )
