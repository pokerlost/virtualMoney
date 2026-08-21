"""Rake-source financial operation projection."""

from __future__ import annotations

from typing import Literal

from domain.enums import FinancialOperationSource
from domain.types import NonNilUUID, OperationId, PositiveMoneyMinor, UtcDatetime
from persistence.projections.base import ProjectionModel


class RakeFinancialOperationProjection(ProjectionModel):
    """Expose one completed escrow-to-rake audit."""

    source: Literal[FinancialOperationSource.RAKE]
    operation_id: OperationId
    amount_minor: PositiveMoneyMinor
    asset_id: NonNilUUID
    table_id: NonNilUUID
    hand_id: NonNilUUID
    table_escrow_account_id: NonNilUUID
    rake_account_id: NonNilUUID
    ledger_transaction_id: NonNilUUID
    created_at: UtcDatetime
