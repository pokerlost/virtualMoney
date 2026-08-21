"""Command for closing a table position."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNegativeMoneyMinor, NonNilUUID, OperationId


class CashOutCommand(ValueModel):
    """Close an OPEN position with the authoritative final stack."""

    operation_id: OperationId
    position_id: NonNilUUID
    amount_minor: NonNegativeMoneyMinor
