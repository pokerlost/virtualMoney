"""Command for adding funds to an OPEN table position."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID, OperationId


class ReBuyCommand(ValueModel):
    """Capture a new ACTIVE hold into an existing position."""

    operation_id: OperationId
    position_id: NonNilUUID
    hold_id: NonNilUUID
