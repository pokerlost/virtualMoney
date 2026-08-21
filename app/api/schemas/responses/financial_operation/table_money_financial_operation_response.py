"""Public table-money-source financial operation response."""

from __future__ import annotations

from typing import Literal

from api.schemas.base import ResponseModel
from domain.enums import FinancialOperationSource, TableMoneyOperationType
from domain.types import NonNegativeMoneyMinor, NonNilUUID, OperationId, UtcDatetime


class TableMoneyFinancialOperationResponse(ResponseModel):
    """Expose native table-money audit fields."""

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
