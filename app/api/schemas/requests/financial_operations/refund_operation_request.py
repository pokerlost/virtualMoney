"""Full financial compensation request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.financial_operations import RefundFinancialOperationCommand
from domain.types import OperationId, RefundReason


class RefundOperationRequest(RequestModel):
    """Identify a ledger-backed operation and one full compensation."""

    operation_id: OperationId = Field(description="Stable refund operation UUID.")
    target_operation_id: OperationId = Field(
        description="Business operation to compensate in full.",
    )
    reason: RefundReason = Field(
        description="Bounded non-secret reason; partial amounts are unsupported.",
    )

    def to_command(self) -> RefundFinancialOperationCommand:
        """Map the request to an application command."""
        return RefundFinancialOperationCommand(
            operation_id=self.operation_id,
            target_operation_id=self.target_operation_id,
            reason=self.reason,
        )
