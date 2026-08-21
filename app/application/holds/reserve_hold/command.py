"""Command for reserving available account funds."""

from __future__ import annotations

from typing import Self

from pydantic import model_validator

from domain import ValueModel
from domain.types import (
    NonNilUUID,
    OperationId,
    PositiveMoneyMinor,
    ReferenceType,
    validate_reference_pair,
)


class ReserveHoldCommand(ValueModel):
    """Full hold reserve semantics and stable operation identity."""

    operation_id: OperationId
    account_id: NonNilUUID
    amount_minor: PositiveMoneyMinor
    reference_type: ReferenceType | None = None
    reference_id: NonNilUUID | None = None

    @model_validator(mode="after")
    def validate_reference(self) -> Self:
        """Require both optional business reference fields."""
        validate_reference_pair(self.reference_type, self.reference_id)
        return self
