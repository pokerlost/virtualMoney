"""Command for a full immutable ledger reversal."""

from __future__ import annotations

from typing import Self

from pydantic import model_validator

from domain import ValueModel
from domain.types import (
    LedgerDescription,
    NonNilUUID,
    OperationId,
    ReferenceType,
    validate_reference_pair,
)


class ReverseLedgerTransactionCommand(ValueModel):
    """Full reversal of an existing posted transaction."""

    operation_id: OperationId
    transaction_id: NonNilUUID
    reference_type: ReferenceType | None = None
    reference_id: NonNilUUID | None = None
    description: LedgerDescription | None = None

    @model_validator(mode="after")
    def validate_reference(self) -> Self:
        """Validate optional reversal reference metadata."""
        validate_reference_pair(self.reference_type, self.reference_id)
        return self
