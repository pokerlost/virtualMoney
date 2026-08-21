"""Financial operation lookup request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.financial_operations import GetOperationQuery
from domain.types import OperationId


class GetOperationRequest(RequestModel):
    """Identify one business operation across immutable audit sources."""

    operation_id: OperationId = Field(description="Stable business operation UUID.")

    def to_query(self) -> GetOperationQuery:
        """Map validated transport fields to the application query."""
        return GetOperationQuery(operation_id=self.operation_id)
