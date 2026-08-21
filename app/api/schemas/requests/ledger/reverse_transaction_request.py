"""Full ledger reversal request."""

from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from api.schemas.base import RequestModel
from application.ledger import ReverseLedgerTransactionCommand
from domain.types import (
    LedgerDescription,
    NonNilUUID,
    OperationId,
    ReferenceType,
    validate_reference_pair,
)


class ReverseTransactionRequest(RequestModel):
    """Identify the original journal and one new reversal operation."""

    operation_id: OperationId = Field(description="Stable reversal operation UUID.")
    transaction_id: NonNilUUID = Field(description="Original ledger transaction UUID.")
    reference_type: ReferenceType | None = Field(
        default=None,
        description="Optional business namespace supplied with referenceId.",
    )
    reference_id: NonNilUUID | None = Field(
        default=None,
        description="Optional business UUID supplied with referenceType.",
    )
    description: LedgerDescription | None = Field(
        default=None,
        description="Optional explanation for the full reversal.",
    )

    @model_validator(mode="after")
    def validate_reference_pair(self) -> Self:
        """Require both optional reference fields."""
        validate_reference_pair(self.reference_type, self.reference_id)
        return self

    def to_command(self) -> ReverseLedgerTransactionCommand:
        """Map the request to an application command."""
        return ReverseLedgerTransactionCommand(
            operation_id=self.operation_id,
            transaction_id=self.transaction_id,
            reference_type=self.reference_type,
            reference_id=self.reference_id,
            description=self.description,
        )
