"""Account balance query."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID


class GetAccountBalanceQuery(ValueModel):
    """Identify the account whose balance projection is requested."""

    account_id: NonNilUUID
