"""Account financial history request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from api.schemas.requests.pagination_request import PaginationRequest
from application.accounts import GetFinancialHistoryQuery
from domain.types import NonNilUUID


class GetFinancialHistoryRequest(RequestModel):
    """Identify an account and one bounded history page."""

    account_id: NonNilUUID = Field(description="Stable service-owned account UUID.")
    pagination: PaginationRequest = Field(
        default_factory=PaginationRequest,
        description="Cursor pagination input.",
    )

    def to_query(self) -> GetFinancialHistoryQuery:
        """Map validated transport fields to the history query."""
        return GetFinancialHistoryQuery(
            account_id=self.account_id,
            pagination=self.pagination.to_application(),
        )
