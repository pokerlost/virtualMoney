"""Public immutable rake operation schema."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import ORMSchema
from domain.types import NonNilUUID, OperationId, PositiveMoneyMinor, UtcDatetime


class RakeOperationSchema(ORMSchema):
    """Expose a completed escrow-to-rake transfer without fingerprint data."""

    id: NonNilUUID
    operation_id: OperationId = Field(description="Stable business operation UUID.")
    table_id: NonNilUUID = Field(description="Opaque Poker Server table UUID.")
    hand_id: NonNilUUID = Field(description="Opaque Poker Server hand UUID.")
    asset_id: NonNilUUID
    table_escrow_account_id: NonNilUUID = Field(description="Debited account UUID.")
    rake_account_id: NonNilUUID = Field(description="Credited system account UUID.")
    amount_minor: PositiveMoneyMinor
    ledger_transaction_id: NonNilUUID = Field(description="RAKE journal UUID.")
    created_at: UtcDatetime
