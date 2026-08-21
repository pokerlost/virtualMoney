"""Account lookup query."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID


class GetAccountQuery(ValueModel):
    """Identify one financial account for lookup."""

    account_id: NonNilUUID
