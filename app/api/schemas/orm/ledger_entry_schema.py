"""Public immutable ledger entry schema."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import ORMSchema
from domain.types import NonNilUUID, NonZeroMoneyMinor, UtcDatetime


class LedgerEntrySchema(ORMSchema):
    """Expose one signed posting in a journal."""

    id: NonNilUUID = Field(description="Stable ledger entry UUID.")
    ledger_transaction_id: NonNilUUID = Field(description="Owning journal UUID.")
    account_id: NonNilUUID = Field(description="Affected financial account UUID.")
    amount_minor: NonZeroMoneyMinor = Field(description="Non-zero signed minimal units.")
    sequence: int = Field(strict=True, ge=1, description="Order within the journal.")
    created_at: UtcDatetime = Field(description="Creation timestamp in UTC.")
