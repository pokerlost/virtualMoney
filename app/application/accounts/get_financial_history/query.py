"""Account financial history query."""

from __future__ import annotations

from application.pagination import PaginationInput
from domain import ValueModel
from domain.types import NonNilUUID


class GetFinancialHistoryQuery(ValueModel):
    """Describe one bounded account-history page."""

    account_id: NonNilUUID
    pagination: PaginationInput
