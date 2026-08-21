"""Table BuyIn use case."""

from __future__ import annotations

import logfire

from application.errors import (
    BuyInHoldInvalid,
    HoldNotFound,
    TableMoneyDataIntegrityError,
    TablePositionAlreadyOpen,
)
from application.fingerprinting import fingerprint_buy_in
from application.holds import HoldCapture
from application.table_positions.services import (
    TableEscrowProvisioner,
    find_table_operation_replay,
    save_table_operation,
    validate_buy_in_source,
)
from domain.enums import HoldStatus, TableMoneyOperationType
from persistence.database.models import PlayerTablePositionModel
from persistence.repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyHoldRepository,
    SQLAlchemyTableMoneyOperationRepository,
    SQLAlchemyTablePositionRepository,
)

from .command import BuyInCommand


class BuyInHandler:
    """Capture an initial hold into escrow and open a position."""

    def __init__(
        self,
        accounts: SQLAlchemyAccountRepository,
        holds: SQLAlchemyHoldRepository,
        positions: SQLAlchemyTablePositionRepository,
        operations: SQLAlchemyTableMoneyOperationRepository,
        hold_capture: HoldCapture,
        escrow_provisioner: TableEscrowProvisioner,
    ) -> None:
        """Store request-scoped collaborators."""
        self._accounts = accounts
        self._holds = holds
        self._positions = positions
        self._operations = operations
        self._hold_capture = hold_capture
        self._escrow_provisioner = escrow_provisioner

    async def execute(self, command: BuyInCommand) -> PlayerTablePositionModel:
        """Open a position or return an exact operation replay."""
        fingerprint = fingerprint_buy_in(command)
        operation_type = TableMoneyOperationType.BUY_IN
        replay = await find_table_operation_replay(
            command.operation_id,
            expected_type=operation_type,
            expected_fingerprint=fingerprint,
            operations=self._operations,
            positions=self._positions,
        )
        if replay is not None:
            return replay

        hold = await self._holds.get_by_id_for_update(command.hold_id)
        if hold is None:
            raise HoldNotFound()
        replay = await find_table_operation_replay(
            command.operation_id,
            expected_type=operation_type,
            expected_fingerprint=fingerprint,
            operations=self._operations,
            positions=self._positions,
        )
        if replay is not None:
            return replay
        if hold.status is not HoldStatus.ACTIVE:
            raise BuyInHoldInvalid()

        source = await self._accounts.get_by_id(hold.account_id)
        if source is None:
            raise TableMoneyDataIntegrityError()
        validate_buy_in_source(source, command)

        escrow = await self._escrow_provisioner.get_or_create(
            table_id=command.table_id,
            asset_id=source.asset_id,
        )
        existing_open = await self._positions.get_open(
            command.user_id,
            command.table_id,
            source.asset_id,
        )
        if existing_open is not None:
            replay = await find_table_operation_replay(
                command.operation_id,
                expected_type=operation_type,
                expected_fingerprint=fingerprint,
                operations=self._operations,
                positions=self._positions,
            )
            if replay is not None:
                return replay
            raise TablePositionAlreadyOpen()

        position = await self._positions.try_add_open(
            user_id=command.user_id,
            table_id=command.table_id,
            asset_id=source.asset_id,
            user_account_id=source.id,
            table_escrow_account_id=escrow.id,
            total_buy_in_minor=hold.amount_minor,
        )
        if position is None:
            raise TablePositionAlreadyOpen()

        capture_result = await self._hold_capture.capture(
            operation_id=command.operation_id,
            hold=hold,
            destination_account_id=escrow.id,
            payload_fingerprint=fingerprint,
        )
        await save_table_operation(
            operations=self._operations,
            operation_id=command.operation_id,
            position_id=position.id,
            operation_type=operation_type,
            payload_fingerprint=fingerprint,
            hold_id=hold.id,
            ledger_transaction_id=capture_result.ledger_transaction.id,
            amount_minor=hold.amount_minor,
        )
        logfire.info(
            "Table BuyIn completed",
            operation_id=str(command.operation_id),
            position_id=str(position.id),
            table_id=str(position.table_id),
            user_id=str(position.user_id),
        )
        return position
