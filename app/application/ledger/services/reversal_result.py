"""Result of the no-commit ledger reversal primitive."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID
from persistence.database.models import LedgerTransactionModel


class LedgerReversalResult(ValueModel):
    """Reversal transaction, projection updates, and replay marker."""

    transaction: LedgerTransactionModel
    updated_account_ids: list[NonNilUUID]
    idempotent_replay: bool
