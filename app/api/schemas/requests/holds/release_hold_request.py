"""Full hold release request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.holds import ReleaseHoldCommand
from domain.types import NonNilUUID, OperationId


class ReleaseHoldRequest(RequestModel):
    """Identify one ACTIVE hold and one release operation."""

    operation_id: OperationId = Field(description="Stable release operation UUID.")
    hold_id: NonNilUUID = Field(description="Hold to release in full.")

    def to_command(self) -> ReleaseHoldCommand:
        """Map the request to an application command."""
        return ReleaseHoldCommand(
            operation_id=self.operation_id,
            hold_id=self.hold_id,
        )
