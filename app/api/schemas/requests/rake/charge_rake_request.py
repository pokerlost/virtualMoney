"""Rake charge request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.rake import ChargeRakeCommand
from domain.types import NonNilUUID, OperationId, PositiveMoneyMinor


class ChargeRakeRequest(RequestModel):
    """Accept a trusted Poker Server rake amount and references."""

    operation_id: OperationId = Field(description="Stable rake operation UUID.")
    table_id: NonNilUUID = Field(description="Opaque Poker Server table UUID.")
    hand_id: NonNilUUID = Field(description="Opaque Poker Server hand UUID.")
    asset_id: NonNilUUID = Field(description="Authoritative internal asset UUID.")
    amount_minor: PositiveMoneyMinor = Field(
        description="Positive amount calculated by Poker Server.",
    )

    def to_command(self) -> ChargeRakeCommand:
        """Map the request to an application command."""
        return ChargeRakeCommand(
            operation_id=self.operation_id,
            table_id=self.table_id,
            hand_id=self.hand_id,
            asset_id=self.asset_id,
            amount_minor=self.amount_minor,
        )
