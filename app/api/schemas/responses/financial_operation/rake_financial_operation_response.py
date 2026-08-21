"""Public rake-source financial operation response."""

from __future__ import annotations

from typing import Literal

from api.schemas.base import ResponseModel
from domain.enums import FinancialOperationSource
from domain.types import NonNilUUID, OperationId, PositiveMoneyMinor, UtcDatetime


class RakeFinancialOperationResponse(ResponseModel):
    """Expose one completed rake audit."""

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
