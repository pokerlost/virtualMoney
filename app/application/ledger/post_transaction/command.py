"""Command for posting an immutable ledger adjustment."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from domain import ValueModel
from domain.enums import LedgerTransactionType
from domain.ledger import MAX_LEDGER_ENTRIES, Posting, validate_postings
from domain.types import (
    LedgerDescription,
    NonNilUUID,
    OperationId,
    ReferenceType,
    validate_reference_pair,
)


class PostLedgerTransactionCommand(ValueModel):
    """One atomic signed double-entry adjustment."""

    operation_id: OperationId
    transaction_type: Literal[LedgerTransactionType.ADJUSTMENT]
    postings: tuple[Posting, ...] = Field(min_length=2, max_length=MAX_LEDGER_ENTRIES)
    reference_type: ReferenceType | None = None
    reference_id: NonNilUUID | None = None
    description: LedgerDescription | None = None

    @model_validator(mode="after")
    def validate_transaction(self) -> Self:
        """Validate the balanced adjustment payload."""
        validate_postings(self.postings)
        validate_reference_pair(self.reference_type, self.reference_id)
        return self
