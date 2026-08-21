"""Command for full financial compensation."""

from __future__ import annotations

from domain import ValueModel
from domain.types import OperationId, RefundReason


class RefundFinancialOperationCommand(ValueModel):
    """Fully compensate an eligible ledger-backed operation."""

    operation_id: OperationId
    target_operation_id: OperationId
    reason: RefundReason
