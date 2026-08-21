"""Public immutable ledger transaction schema."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import ORMSchema
from api.schemas.orm.ledger_entry_schema import LedgerEntrySchema
from domain.enums import LedgerTransactionStatus, LedgerTransactionType
from domain.ledger import MAX_LEDGER_ENTRIES
from domain.types import (
    LedgerDescription,
    NonNilUUID,
    OperationId,
    ReferenceType,
    UtcDatetime,
)


class LedgerTransactionSchema(ORMSchema):
    """Expose a posted journal and all eagerly materialized entries."""

    id: NonNilUUID = Field(description="Stable journal UUID.")
    operation_id: OperationId = Field(description="Stable business operation UUID.")
    asset_id: NonNilUUID = Field(description="Asset shared by every entry.")
    transaction_type: LedgerTransactionType
    status: LedgerTransactionStatus
    reference_type: ReferenceType | None
    reference_id: NonNilUUID | None
    description: LedgerDescription | None
    reversal_of_transaction_id: NonNilUUID | None
    created_at: UtcDatetime
    posted_at: UtcDatetime
    entries: list[LedgerEntrySchema] = Field(
        min_length=2,
        max_length=MAX_LEDGER_ENTRIES,
        description="Ordered immutable entries with a zero-sum invariant.",
    )
