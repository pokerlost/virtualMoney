"""Command for fully capturing a hold."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID, OperationId


class CaptureHoldCommand(ValueModel):
    """Full capture semantics without a caller-supplied amount."""

    operation_id: OperationId
    hold_id: NonNilUUID
    destination_account_id: NonNilUUID
