"""Ledger transaction lookup request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.ledger import GetTransactionQuery
from domain.types import NonNilUUID


class GetTransactionRequest(RequestModel):
    """Identify one immutable ledger transaction."""

    transaction_id: NonNilUUID = Field(description="Stable ledger transaction UUID.")

    def to_query(self) -> GetTransactionQuery:
        """Map validated transport fields to the application query."""
        return GetTransactionQuery(transaction_id=self.transaction_id)
