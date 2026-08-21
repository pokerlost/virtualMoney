"""Ledger-source financial operation projection."""

from __future__ import annotations

from typing import Literal

from domain.enums import (
    FinancialOperationSource,
    LedgerTransactionStatus,
    LedgerTransactionType,
)
from domain.types import (
    NonNilUUID,
    OperationId,
    ReferenceType,
    UtcDatetime,
)
from persistence.projections.base import ProjectionModel


class LedgerFinancialOperationProjection(ProjectionModel):
    """Expose native immutable ledger operation semantics."""

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
