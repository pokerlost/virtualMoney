"""Public account history item response."""

from __future__ import annotations

from api.schemas.base import ResponseModel
from domain.enums import LedgerTransactionType
from domain.types import (
    NonNilUUID,
    OperationId,
    ReferenceType,
    SignedMoneyMinor,
    UtcDatetime,
)


class AccountHistoryItemResponse(ResponseModel):
    """Expose one account-relative immutable ledger row."""

    ledger_transaction_id: NonNilUUID
    operation_id: OperationId
    transaction_type: LedgerTransactionType
    amount_minor: SignedMoneyMinor
    reference_type: ReferenceType | None
    reference_id: NonNilUUID | None
    posted_at: UtcDatetime
    reversal_of_transaction_id: NonNilUUID | None
    reversed_by_transaction_id: NonNilUUID | None
    is_reversal: bool
