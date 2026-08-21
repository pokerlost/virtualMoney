"""Hold reservation request."""

from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from api.schemas.base import RequestModel
from application.holds import ReserveHoldCommand
from domain.types import (
    NonNilUUID,
    OperationId,
    PositiveMoneyMinor,
    ReferenceType,
    validate_reference_pair,
)


class ReserveHoldRequest(RequestModel):
    """Accept one full reserve amount and optional business reference."""

    operation_id: OperationId = Field(description="Stable reserve operation UUID.")
    account_id: NonNilUUID = Field(description="ACTIVE USER source account UUID.")
    amount_minor: PositiveMoneyMinor = Field(
        description="Positive amount in the account asset's minimal units.",
    )
    reference_type: ReferenceType | None = Field(
        default=None,
        description="Optional business namespace supplied with referenceId.",
    )
    reference_id: NonNilUUID | None = Field(
        default=None,
        description="Optional business UUID supplied with referenceType.",
    )

    @model_validator(mode="after")
    def validate_reference_pair(self) -> Self:
        """Require both optional reference fields."""
        validate_reference_pair(self.reference_type, self.reference_id)
        return self

    def to_command(self) -> ReserveHoldCommand:
        """Map the request to an application command."""
        return ReserveHoldCommand(
            operation_id=self.operation_id,
            account_id=self.account_id,
            amount_minor=self.amount_minor,
            reference_type=self.reference_type,
            reference_id=self.reference_id,
        )
