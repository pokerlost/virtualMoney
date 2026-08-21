"""Command for charging Poker Server calculated rake."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID, OperationId, PositiveMoneyMinor


class ChargeRakeCommand(ValueModel):
    """Transfer a trusted positive amount from table escrow to rake."""

    operation_id: OperationId
    table_id: NonNilUUID
    asset_id: NonNilUUID
    amount_minor: PositiveMoneyMinor
    hand_id: NonNilUUID
