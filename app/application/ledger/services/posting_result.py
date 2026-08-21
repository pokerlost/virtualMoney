"""Result of the no-commit ledger posting primitive."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID
from persistence.database.models import LedgerTransactionModel


class LedgerPostingResult(ValueModel):
    """Ledger aggregate and projections changed by the posting."""

    transaction: LedgerTransactionModel
    updated_account_ids: list[NonNilUUID]
