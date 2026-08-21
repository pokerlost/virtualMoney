"""Table-position operation history projection."""

from __future__ import annotations

from domain.enums import TableMoneyOperationType
from domain.types import (
    NonNegativeMoneyMinor,
    NonNilUUID,
    OperationId,
    UtcDatetime,
)

from .base import ProjectionModel


class TablePositionOperationProjection(ProjectionModel):
    """Represent one immutable BuyIn, ReBuy, or CashOut audit."""

    operation_id: OperationId
    operation_type: TableMoneyOperationType
    amount_minor: NonNegativeMoneyMinor
    hold_id: NonNilUUID | None
    ledger_transaction_id: NonNilUUID | None
    created_at: UtcDatetime
