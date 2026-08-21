"""Table BuyIn request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.table_positions import BuyInCommand
from domain.types import NonNilUUID, OperationId


class BuyInRequest(RequestModel):
    """Open a position through full capture of an ACTIVE hold."""

    operation_id: OperationId = Field(description="Stable BuyIn operation UUID.")
    hold_id: NonNilUUID = Field(description="ACTIVE hold captured into table escrow.")
    user_id: NonNilUUID = Field(description="Opaque Poker Server player UUID.")
    table_id: NonNilUUID = Field(description="Opaque Poker Server table UUID.")

    def to_command(self) -> BuyInCommand:
        """Map the request to an application command."""
        return BuyInCommand(
            operation_id=self.operation_id,
            hold_id=self.hold_id,
            user_id=self.user_id,
            table_id=self.table_id,
        )
