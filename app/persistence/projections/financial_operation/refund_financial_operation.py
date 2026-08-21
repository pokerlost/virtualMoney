"""Refund-source financial operation projection."""

from __future__ import annotations

from typing import Literal

from domain.enums import FinancialOperationSource
from domain.types import NonNilUUID, OperationId, RefundReason, UtcDatetime
from persistence.projections.base import ProjectionModel


class RefundFinancialOperationProjection(ProjectionModel):
    """Expose one completed full compensation audit."""

    source: Literal[FinancialOperationSource.REFUND]
    operation_id: OperationId
    target_operation_id: OperationId
    asset_id: NonNilUUID
    original_ledger_transaction_id: NonNilUUID
    reversal_ledger_transaction_id: NonNilUUID
    reason: RefundReason
    created_at: UtcDatetime
