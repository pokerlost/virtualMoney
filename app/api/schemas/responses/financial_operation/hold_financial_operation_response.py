"""Public hold-source financial operation response."""

from __future__ import annotations

from typing import Literal

from api.schemas.base import ResponseModel
from domain.enums import FinancialOperationSource, HoldOperationType
from domain.types import NonNilUUID, OperationId, PositiveMoneyMinor, UtcDatetime


class HoldFinancialOperationResponse(ResponseModel):
    """Expose native hold audit fields."""

    source: Literal[FinancialOperationSource.HOLD]
    operation_id: OperationId
    operation_type: HoldOperationType
    amount_minor: PositiveMoneyMinor
    asset_id: NonNilUUID
    account_id: NonNilUUID
    hold_id: NonNilUUID
    ledger_transaction_id: NonNilUUID | None
    created_at: UtcDatetime
