"""Command for fully releasing a hold."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID, OperationId


class ReleaseHoldCommand(ValueModel):
    """Full release semantics and stable operation identity."""

    operation_id: OperationId
    hold_id: NonNilUUID
