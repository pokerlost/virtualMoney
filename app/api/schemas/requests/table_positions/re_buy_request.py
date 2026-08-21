"""Table ReBuy request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.table_positions import ReBuyCommand
from domain.types import NonNilUUID, OperationId


class ReBuyRequest(RequestModel):
    """Capture another ACTIVE hold into an OPEN position."""

    operation_id: OperationId = Field(description="Stable ReBuy operation UUID.")
    position_id: NonNilUUID = Field(description="OPEN durable table-position UUID.")
    hold_id: NonNilUUID = Field(description="New hold for the position's USER account.")

    def to_command(self) -> ReBuyCommand:
        """Map the request to an application command."""
        return ReBuyCommand(
            operation_id=self.operation_id,
            position_id=self.position_id,
            hold_id=self.hold_id,
        )
