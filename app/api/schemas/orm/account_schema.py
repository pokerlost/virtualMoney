"""Public account entity schema."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import ORMSchema
from domain.enums import AccountStatus, AccountType, OwnerType
from domain.types import NonNilUUID, UtcDatetime


class AccountSchema(ORMSchema):
    """Expose account metadata without an embedded balance."""

    id: NonNilUUID = Field(description="Stable service-owned account UUID.")
    asset_id: NonNilUUID = Field(description="Authoritative internal asset UUID.")
    account_type: AccountType = Field(description="Accounting purpose of the account.")
    owner_type: OwnerType = Field(description="Namespace of the opaque owner UUID.")
    owner_id: NonNilUUID | None = Field(
        description="Opaque owner UUID, or null for a SYSTEM-owned account.",
    )
    status: AccountStatus = Field(description="Availability for future operations.")
    created_at: UtcDatetime = Field(description="Creation timestamp in UTC.")
    updated_at: UtcDatetime = Field(description="Last metadata update timestamp in UTC.")
