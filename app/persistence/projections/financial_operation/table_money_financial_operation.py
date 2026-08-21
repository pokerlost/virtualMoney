"""Table-money-source financial operation projection."""

from __future__ import annotations

from typing import Literal

from domain.enums import FinancialOperationSource, TableMoneyOperationType
from domain.types import (
    NonNegativeMoneyMinor,
    NonNilUUID,
    OperationId,
    UtcDatetime,
)
from persistence.projections.base import ProjectionModel


class TableMoneyFinancialOperationProjection(ProjectionModel):
    """Expose one native table-money audit operation."""

    source: Literal[FinancialOperationSource.TABLE_MONEY]
    operation_id: OperationId
    operation_type: TableMoneyOperationType
    amount_minor: NonNegativeMoneyMinor
    asset_id: NonNilUUID
    account_id: NonNilUUID
    table_id: NonNilUUID
    position_id: NonNilUUID
    hold_id: NonNilUUID | None
    ledger_transaction_id: NonNilUUID | None
    created_at: UtcDatetime
