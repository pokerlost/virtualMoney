"""Account lookup request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.accounts import GetAccountQuery
from domain.types import NonNilUUID


class GetAccountRequest(RequestModel):
    """Identify one financial account."""

    account_id: NonNilUUID = Field(description="Stable service-owned account UUID.")

    def to_query(self) -> GetAccountQuery:
        """Map validated transport fields to the account query."""
        return GetAccountQuery(account_id=self.account_id)
