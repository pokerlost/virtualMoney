"""One signed ledger posting request item."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from domain.ledger import Posting
from domain.types import NonNilUUID, NonZeroMoneyMinor


class LedgerPostingRequest(RequestModel):
    """Describe one non-zero account change in minimal units."""

    account_id: NonNilUUID = Field(description="Participating financial account UUID.")
    amount_minor: NonZeroMoneyMinor = Field(
        description="Negative decreases and positive increases the account position.",
    )

    def to_posting(self) -> Posting:
        """Map the request item to a domain posting."""
        return Posting(account_id=self.account_id, amount_minor=self.amount_minor)
