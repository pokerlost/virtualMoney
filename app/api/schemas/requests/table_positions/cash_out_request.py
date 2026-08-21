"""Table CashOut request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.table_positions import CashOutCommand
from domain.types import NonNegativeMoneyMinor, NonNilUUID, OperationId


class CashOutRequest(RequestModel):
    """Close a position using the authoritative Poker Server final stack."""

    operation_id: OperationId = Field(description="Stable CashOut operation UUID.")
    position_id: NonNilUUID = Field(description="OPEN durable table-position UUID.")
    amount_minor: NonNegativeMoneyMinor = Field(
        description="Final stack; zero closes without creating zero-value entries.",
    )

    def to_command(self) -> CashOutCommand:
        """Map the request to an application command."""
        return CashOutCommand(
            operation_id=self.operation_id,
            position_id=self.position_id,
            amount_minor=self.amount_minor,
        )
