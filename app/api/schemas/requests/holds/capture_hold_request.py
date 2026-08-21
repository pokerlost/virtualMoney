"""Full hold capture request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.holds import CaptureHoldCommand
from domain.types import NonNilUUID, OperationId


class CaptureHoldRequest(RequestModel):
    """Identify one ACTIVE hold and its destination account."""

    operation_id: OperationId = Field(description="Stable capture operation UUID.")
    hold_id: NonNilUUID = Field(description="Hold to capture in full.")
    destination_account_id: NonNilUUID = Field(
        description="Same-asset account receiving the entire held amount.",
    )

    def to_command(self) -> CaptureHoldCommand:
        """Map the request to an application command."""
        return CaptureHoldCommand(
            operation_id=self.operation_id,
            hold_id=self.hold_id,
            destination_account_id=self.destination_account_id,
        )
