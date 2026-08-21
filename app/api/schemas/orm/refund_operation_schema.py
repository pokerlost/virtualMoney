"""Public immutable refund audit schema."""

from __future__ import annotations

from api.schemas.base import ORMSchema
from domain.types import NonNilUUID, OperationId, RefundReason, UtcDatetime


class RefundOperationSchema(ORMSchema):
    """Expose a completed full compensation without fingerprint data."""

    id: NonNilUUID
    operation_id: OperationId
    target_operation_id: OperationId
    original_ledger_transaction_id: NonNilUUID
    reversal_ledger_transaction_id: NonNilUUID
    reason: RefundReason
    created_at: UtcDatetime
