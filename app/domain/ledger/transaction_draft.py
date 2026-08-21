"""Validated ledger transaction draft."""

from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from domain.enums import LedgerTransactionType
from domain.errors import InvalidLedgerTransaction
from domain.types import (
    LedgerDescription,
    NonNilUUID,
    OperationId,
    ReferenceType,
    validate_reference_pair,
)
from domain.value_model import ValueModel

from .posting import Posting
from .validation import MAX_LEDGER_ENTRIES, validate_postings


class LedgerTransactionDraft(ValueModel):
    """Semantic payload of a ledger transaction before persistence."""

    operation_id: OperationId
    transaction_type: LedgerTransactionType
    postings: tuple[Posting, ...] = Field(
        min_length=2,
        max_length=MAX_LEDGER_ENTRIES,
    )
    reference_type: ReferenceType | None = None
    reference_id: NonNilUUID | None = None
    description: LedgerDescription | None = None
    reversal_of_transaction_id: NonNilUUID | None = None

    @model_validator(mode="after")
    def validate_transaction(self) -> Self:
        """Validate balanced postings, references, and reversal metadata."""
        validate_postings(self.postings)
        validate_reference_pair(self.reference_type, self.reference_id)
        if self.transaction_type is LedgerTransactionType.REVERSAL:
            if self.reversal_of_transaction_id is None:
                raise InvalidLedgerTransaction(
                    "reversal must reference the original transaction",
                )
        elif self.reversal_of_transaction_id is not None:
            raise InvalidLedgerTransaction(
                "non-reversal transaction cannot reference a reversed transaction",
            )
        return self
