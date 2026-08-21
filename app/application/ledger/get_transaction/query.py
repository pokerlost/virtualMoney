"""Ledger transaction lookup query."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID


class GetTransactionQuery(ValueModel):
    """Identify one immutable ledger transaction for lookup."""

    transaction_id: NonNilUUID
