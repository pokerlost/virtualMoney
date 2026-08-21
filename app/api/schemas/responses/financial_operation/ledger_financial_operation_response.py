"""Public ledger-source financial operation response."""

from __future__ import annotations

from typing import Literal

from api.schemas.base import ResponseModel
from domain.enums import (
    FinancialOperationSource,
    LedgerTransactionStatus,
    LedgerTransactionType,
)
from domain.types import NonNilUUID, OperationId, ReferenceType, UtcDatetime


class LedgerFinancialOperationResponse(ResponseModel):
    """Expose native ledger operation fields."""

    source: Literal[FinancialOperationSource.LEDGER]
    operation_id: OperationId
    operation_type: LedgerTransactionType
    status: LedgerTransactionStatus
    asset_id: NonNilUUID
    reference_type: ReferenceType | None
    reference_id: NonNilUUID | None
    ledger_transaction_id: NonNilUUID
    reversal_of_transaction_id: NonNilUUID | None
    created_at: UtcDatetime
