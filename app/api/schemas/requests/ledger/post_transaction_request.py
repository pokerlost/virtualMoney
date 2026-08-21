"""Ledger posting request."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from api.schemas.base import RequestModel
from application.ledger import PostLedgerTransactionCommand
from domain.enums import LedgerTransactionType
from domain.ledger import MAX_LEDGER_ENTRIES
from domain.types import (
    LedgerDescription,
    NonNilUUID,
    OperationId,
    ReferenceType,
    validate_reference_pair,
)

from .ledger_posting_request import LedgerPostingRequest


class PostTransactionRequest(RequestModel):
    """Accept one balanced low-level ADJUSTMENT journal."""

    operation_id: OperationId = Field(description="Stable business operation UUID.")
    transaction_type: Literal[LedgerTransactionType.ADJUSTMENT] = Field(
        description="This endpoint accepts only ADJUSTMENT.",
    )
    postings: list[LedgerPostingRequest] = Field(
        min_length=2,
        max_length=MAX_LEDGER_ENTRIES,
        description="Ordered same-asset postings whose signed sum is zero.",
    )
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
        description="Optional operator-facing context.",
    )

    @model_validator(mode="after")
    def validate_reference_pair(self) -> Self:
        """Require both optional reference fields."""
        validate_reference_pair(self.reference_type, self.reference_id)
        return self

    def to_command(self) -> PostLedgerTransactionCommand:
        """Map the request to an application command."""
        return PostLedgerTransactionCommand(
            operation_id=self.operation_id,
            transaction_type=self.transaction_type,
            postings=tuple(posting.to_posting() for posting in self.postings),
            reference_type=self.reference_type,
            reference_id=self.reference_id,
            description=self.description,
        )
