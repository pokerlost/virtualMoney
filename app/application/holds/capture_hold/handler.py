"""Hold capture use case."""

from __future__ import annotations

import logfire

from application.errors import HoldNotFound
from application.fingerprinting import fingerprint_capture_hold
from application.holds.services import HoldCapture, find_hold_replay
from domain.enums import HoldOperationType
from persistence.database.models import HoldModel
from persistence.repositories import SQLAlchemyHoldOperationRepository, SQLAlchemyHoldRepository

from .command import CaptureHoldCommand


class CaptureHoldHandler:
    """Turn one full hold into a HOLD_CAPTURE ledger transfer."""

    def __init__(
        self,
        holds: SQLAlchemyHoldRepository,
        hold_operations: SQLAlchemyHoldOperationRepository,
        hold_capture: HoldCapture,
    ) -> None:
        """Store request-scoped collaborators."""
        self._holds = holds
        self._hold_operations = hold_operations
        self._hold_capture = hold_capture

    async def execute(self, command: CaptureHoldCommand) -> HoldModel:
        """Capture the authoritative hold amount or return an exact replay."""
        fingerprint = fingerprint_capture_hold(command)
        replay = await find_hold_replay(
            command.operation_id,
            expected_type=HoldOperationType.CAPTURE,
            expected_fingerprint=fingerprint,
            operations=self._hold_operations,
            holds=self._holds,
        )
        if replay is not None:
            return replay

        hold = await self._holds.get_by_id_for_update(command.hold_id)
        if hold is None:
            raise HoldNotFound()
        replay = await find_hold_replay(
            command.operation_id,
            expected_type=HoldOperationType.CAPTURE,
            expected_fingerprint=fingerprint,
            operations=self._hold_operations,
            holds=self._holds,
        )
        if replay is not None:
            return replay

        result = await self._hold_capture.capture(
            operation_id=command.operation_id,
            hold=hold,
            destination_account_id=command.destination_account_id,
            payload_fingerprint=fingerprint,
        )
        captured = result.hold
        logfire.info(
            "Funds hold captured",
            destination_account_id=str(command.destination_account_id),
            hold_id=str(captured.id),
            ledger_transaction_id=str(result.ledger_transaction.id),
            operation_id=str(command.operation_id),
        )
        return captured
