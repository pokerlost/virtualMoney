"""Full hold release use case."""

from __future__ import annotations

import logfire

from application.accounts.services import AccountBalanceProjection, BalanceProjectionDelta
from application.errors import (
    HoldAlreadyCaptured,
    HoldAlreadyReleased,
    HoldNotFound,
    HoldWriteConflict,
    InvalidHoldState,
)
from application.fingerprinting import fingerprint_release_hold
from application.holds.services import find_hold_replay
from domain.enums import HoldOperationType, HoldStatus
from persistence.database.models import HoldModel
from persistence.repositories import SQLAlchemyHoldOperationRepository, SQLAlchemyHoldRepository

from .command import ReleaseHoldCommand


def _raise_terminal_state(hold: HoldModel) -> None:
    if hold.status is HoldStatus.RELEASED:
        raise HoldAlreadyReleased()
    if hold.status is HoldStatus.CAPTURED:
        raise HoldAlreadyCaptured()
    raise InvalidHoldState()


class ReleaseHoldHandler:
    """Release an ACTIVE hold in full without a ledger posting."""

    def __init__(
        self,
        holds: SQLAlchemyHoldRepository,
        hold_operations: SQLAlchemyHoldOperationRepository,
        balance_projection: AccountBalanceProjection,
    ) -> None:
        """Store request-scoped collaborators."""
        self._holds = holds
        self._hold_operations = hold_operations
        self._balance_projection = balance_projection

    async def execute(self, command: ReleaseHoldCommand) -> HoldModel:
        """Decrease held funds and transition the hold to RELEASED."""
        fingerprint = fingerprint_release_hold(command)
        replay = await find_hold_replay(
            command.operation_id,
            expected_type=HoldOperationType.RELEASE,
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
            expected_type=HoldOperationType.RELEASE,
            expected_fingerprint=fingerprint,
            operations=self._hold_operations,
            holds=self._holds,
        )
        if replay is not None:
            return replay
        if hold.status is not HoldStatus.ACTIVE:
            _raise_terminal_state(hold)

        balances = await self._balance_projection.lock([hold.account_id])
        inserted = await self._hold_operations.insert_if_absent(
            command.operation_id,
            hold.id,
            HoldOperationType.RELEASE,
            fingerprint,
            None,
        )
        if not inserted:
            replay = await find_hold_replay(
                command.operation_id,
                expected_type=HoldOperationType.RELEASE,
                expected_fingerprint=fingerprint,
                operations=self._hold_operations,
                holds=self._holds,
            )
            if replay is None:
                raise HoldWriteConflict()
            return replay

        await self._balance_projection.apply(
            [
                BalanceProjectionDelta(
                    account_id=hold.account_id,
                    held_delta_minor=-hold.amount_minor,
                ),
            ],
            locked_balances=balances,
        )
        released = await self._holds.save_released(hold.id)
        if released is None:
            raise HoldWriteConflict()
        logfire.info(
            "Funds hold released",
            account_id=str(released.account_id),
            hold_id=str(released.id),
            operation_id=str(command.operation_id),
        )
        return released
