"""Result of reusable full hold capture."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID
from persistence.database.models import HoldModel, LedgerTransactionModel


class HoldCaptureResult(ValueModel):
    """Captured hold, ledger transaction, and changed projections."""

    hold: HoldModel
    ledger_transaction: LedgerTransactionModel
    updated_account_ids: list[NonNilUUID]
