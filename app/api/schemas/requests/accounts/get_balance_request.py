"""Account balance lookup request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.accounts import GetAccountBalanceQuery
from domain.types import NonNilUUID


class GetBalanceRequest(RequestModel):
    """Identify the account whose materialized balance is requested."""

    account_id: NonNilUUID = Field(description="Stable service-owned account UUID.")

    def to_query(self) -> GetAccountBalanceQuery:
        """Map validated transport fields to the balance query."""
        return GetAccountBalanceQuery(account_id=self.account_id)
