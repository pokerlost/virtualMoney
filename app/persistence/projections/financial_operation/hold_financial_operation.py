"""Hold-source financial operation projection."""

from __future__ import annotations

from typing import Literal

from domain.enums import FinancialOperationSource, HoldOperationType
from domain.types import (
    NonNilUUID,
    OperationId,
    PositiveMoneyMinor,
    UtcDatetime,
)
from persistence.projections.base import ProjectionModel


class HoldFinancialOperationProjection(ProjectionModel):
    """Expose one native hold audit operation."""

    source: Literal[FinancialOperationSource.HOLD]
    operation_id: OperationId
    operation_type: HoldOperationType
    amount_minor: PositiveMoneyMinor
    asset_id: NonNilUUID
    account_id: NonNilUUID
    hold_id: NonNilUUID
    ledger_transaction_id: NonNilUUID | None
    created_at: UtcDatetime
