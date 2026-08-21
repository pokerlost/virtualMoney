"""Table ReBuy use case."""

from __future__ import annotations

import logfire

from application.errors import (
    AccountBalanceOverflow,
    HoldNotFound,
    ReBuyHoldInvalid,
    TableEscrowUnavailable,
    TableMoneyDataIntegrityError,
    TableMoneyWriteConflict,
    TablePositionClosed,
    TablePositionNotFound,
)
from application.fingerprinting import fingerprint_re_buy
from application.holds import HoldCapture
from application.table_positions.services import (
    find_table_operation_replay,
    save_table_operation,
    validate_position_escrow,
    validate_position_user_account,
)
from domain.enums import (
    AccountStatus,
    HoldStatus,
    PlayerTablePositionStatus,
    TableMoneyOperationType,
)
from domain.money import fits_postgres_bigint
from persistence.database.models import PlayerTablePositionModel
from persistence.repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyHoldRepository,
    SQLAlchemyTableMoneyOperationRepository,
    SQLAlchemyTablePositionRepository,
)

from .command import ReBuyCommand


class ReBuyHandler:
    """Capture another hold and increase the OPEN position total."""

    def __init__(
        self,
        accounts: SQLAlchemyAccountRepository,
        holds: SQLAlchemyHoldRepository,
        positions: SQLAlchemyTablePositionRepository,
        operations: SQLAlchemyTableMoneyOperationRepository,
        hold_capture: HoldCapture,
    ) -> None:
        """Store request-scoped collaborators."""
        self._accounts = accounts
        self._holds = holds
        self._positions = positions
        self._operations = operations
        self._hold_capture = hold_capture

    async def execute(self, command: ReBuyCommand) -> PlayerTablePositionModel:
        """Increase an OPEN position or return an exact replay."""
        fingerprint = fingerprint_re_buy(command)
        operation_type = TableMoneyOperationType.REBUY
        replay = await find_table_operation_replay(
            command.operation_id,
            expected_type=operation_type,
            expected_fingerprint=fingerprint,
            operations=self._operations,
            positions=self._positions,
        )
        if replay is not None:
            return replay

        position = await self._positions.get_by_id_for_update(command.position_id)
        if position is None:
            raise TablePositionNotFound()
        replay = await find_table_operation_replay(
            command.operation_id,
            expected_type=operation_type,
            expected_fingerprint=fingerprint,
            operations=self._operations,
            positions=self._positions,
        )
        if replay is not None:
            return replay
        if position.status is not PlayerTablePositionStatus.OPEN:
            raise TablePositionClosed()

        hold = await self._holds.get_by_id_for_update(command.hold_id)
        if hold is None:
            raise HoldNotFound()
        if hold.status is not HoldStatus.ACTIVE or hold.account_id != position.user_account_id:
            raise ReBuyHoldInvalid()

        source = await self._accounts.get_by_id(position.user_account_id)
        escrow = await self._accounts.get_by_id(position.table_escrow_account_id)
        if source is None or escrow is None:
            raise TableMoneyDataIntegrityError()
        validate_position_user_account(position, source)
        validate_position_escrow(position, escrow)
        if source.status is AccountStatus.CLOSED:
            raise ReBuyHoldInvalid()
        if escrow.status is AccountStatus.CLOSED:
            raise TableEscrowUnavailable()

        total_buy_in_minor = position.total_buy_in_minor + hold.amount_minor
        if not fits_postgres_bigint(total_buy_in_minor):
            raise AccountBalanceOverflow()

        capture_result = await self._hold_capture.capture(
            operation_id=command.operation_id,
            hold=hold,
            destination_account_id=position.table_escrow_account_id,
            payload_fingerprint=fingerprint,
        )
        updated = await self._positions.save_rebuy_total(
            position.id,
            total_buy_in_minor,
        )
        if updated is None:
            raise TableMoneyWriteConflict()
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
            "Table ReBuy completed",
            operation_id=str(command.operation_id),
            position_id=str(updated.id),
            table_id=str(updated.table_id),
            user_id=str(updated.user_id),
        )
        return updated
