"""Public table-position operation history item."""

from __future__ import annotations

from api.schemas.base import ResponseModel
from domain.enums import TableMoneyOperationType
from domain.types import NonNegativeMoneyMinor, NonNilUUID, OperationId, UtcDatetime


class TablePositionOperationResponse(ResponseModel):
    """Expose one immutable BuyIn, ReBuy, or CashOut audit."""

    operation_id: OperationId
    operation_type: TableMoneyOperationType
    amount_minor: NonNegativeMoneyMinor
    hold_id: NonNilUUID | None
    ledger_transaction_id: NonNilUUID | None
    created_at: UtcDatetime
