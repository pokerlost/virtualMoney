"""Command for opening a table position."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID, OperationId


class BuyInCommand(ValueModel):
    """Open a position through full capture of an ACTIVE hold."""

    operation_id: OperationId
    hold_id: NonNilUUID
    user_id: NonNilUUID
    table_id: NonNilUUID
