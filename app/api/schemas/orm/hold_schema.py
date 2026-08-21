"""Public hold entity schema."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import ORMSchema
from domain.enums import HoldStatus
from domain.types import NonNilUUID, PositiveMoneyMinor, ReferenceType, UtcDatetime


class HoldSchema(ORMSchema):
    """Expose the full-only funds hold lifecycle."""

    id: NonNilUUID = Field(description="Stable service-owned hold UUID.")
    account_id: NonNilUUID = Field(description="USER account whose funds are held.")
    amount_minor: PositiveMoneyMinor = Field(description="Immutable full hold amount.")
    status: HoldStatus = Field(description="ACTIVE, RELEASED, or CAPTURED state.")
    reference_type: ReferenceType | None = Field(description="Business reference namespace.")
    reference_id: NonNilUUID | None = Field(description="Opaque business reference UUID.")
    created_at: UtcDatetime = Field(description="Creation timestamp in UTC.")
    updated_at: UtcDatetime = Field(description="Last transition timestamp in UTC.")
    released_at: UtcDatetime | None = Field(description="Full release timestamp or null.")
    captured_at: UtcDatetime | None = Field(description="Full capture timestamp or null.")
    capture_ledger_transaction_id: NonNilUUID | None = Field(
        description="HOLD_CAPTURE ledger transaction UUID or null.",
    )
