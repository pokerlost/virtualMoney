"""Hold reservation use case."""

from __future__ import annotations

import logfire

from application.accounts.services import AccountBalanceProjection, BalanceProjectionDelta
from application.errors import (
    AccountNotFound,
    HoldAccountUnavailable,
    HoldWriteConflict,
    InsufficientAvailableBalance,
)
from application.fingerprinting import fingerprint_reserve_hold
from application.holds.services import find_hold_replay
from domain.enums import AccountStatus, AccountType, HoldOperationType
from persistence.database.models import HoldModel
from persistence.repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyHoldOperationRepository,
    SQLAlchemyHoldRepository,
)

from .command import ReserveHoldCommand


class ReserveHoldHandler:
    """Create an ACTIVE hold and increase held funds atomically."""

    def __init__(
        self,
        accounts: SQLAlchemyAccountRepository,
        holds: SQLAlchemyHoldRepository,
        hold_operations: SQLAlchemyHoldOperationRepository,
        balance_projection: AccountBalanceProjection,
    ) -> None:
        """Store request-scoped collaborators."""
        self._accounts = accounts
        self._holds = holds
        self._hold_operations = hold_operations
        self._balance_projection = balance_projection

    async def execute(self, command: ReserveHoldCommand) -> HoldModel:
        """Reserve available funds or return an exact replay."""
        fingerprint = fingerprint_reserve_hold(command)
        replay = await find_hold_replay(
            command.operation_id,
            expected_type=HoldOperationType.RESERVE,
            expected_fingerprint=fingerprint,
            operations=self._hold_operations,
            holds=self._holds,
        )
        if replay is not None:
            return replay

        account = await self._accounts.get_by_id(command.account_id)
        if account is None:
            raise AccountNotFound()
        if (
            account.account_type is not AccountType.USER
            or account.status is not AccountStatus.ACTIVE
        ):
            raise HoldAccountUnavailable()

        balances = await self._balance_projection.lock([command.account_id])
        replay = await find_hold_replay(
            command.operation_id,
            expected_type=HoldOperationType.RESERVE,
            expected_fingerprint=fingerprint,
            operations=self._hold_operations,
            holds=self._holds,
        )
        if replay is not None:
            return replay

        balance = balances[command.account_id]
        if balance.available_balance_minor < command.amount_minor:
            raise InsufficientAvailableBalance()

        hold = await self._holds.create_hold(
            command.account_id,
            command.amount_minor,
            command.reference_type,
            command.reference_id,
        )
        inserted = await self._hold_operations.insert_if_absent(
            command.operation_id,
            hold.id,
            HoldOperationType.RESERVE,
            fingerprint,
            None,
        )
        if not inserted:
            # The hold row has already been inserted in this transaction. Raising
            # guarantees that the request transaction rolls it back before a retry.
            raise HoldWriteConflict()

        await self._balance_projection.apply(
            [
                BalanceProjectionDelta(
                    account_id=command.account_id,
                    held_delta_minor=command.amount_minor,
                ),
            ],
            locked_balances=balances,
        )
        logfire.info(
            "Funds hold reserved",
            account_id=str(hold.account_id),
            hold_id=str(hold.id),
            operation_id=str(command.operation_id),
        )
        return hold
