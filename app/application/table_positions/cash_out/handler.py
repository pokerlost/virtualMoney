"""Table CashOut use case."""

from __future__ import annotations

from uuid import UUID

import logfire

from application.accounts.services import AccountBalanceProjection, index_accounts_by_id
from application.errors import (
    IdempotencyConflict,
    LedgerAccountUnavailable,
    TableEscrowInsufficientBalance,
    TableEscrowUnavailable,
    TableMoneyDataIntegrityError,
    TableMoneyWriteConflict,
    TablePositionClosed,
    TablePositionNotFound,
)
from application.fingerprinting import fingerprint_cash_out
from application.ledger import LedgerPosting
from application.table_positions.services import (
    find_table_operation_replay,
    save_table_operation,
    validate_position_escrow,
    validate_position_user_account,
)
from domain.enums import (
    AccountStatus,
    LedgerReferenceType,
    LedgerTransactionType,
    PlayerTablePositionStatus,
    TableMoneyOperationType,
)
from domain.ledger import LedgerTransactionDraft, Posting
from persistence.database.models import PlayerTablePositionModel
from persistence.repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyLedgerRepository,
    SQLAlchemyTableMoneyOperationRepository,
    SQLAlchemyTablePositionRepository,
)

from .command import CashOutCommand


class CashOutHandler:
    """Close an OPEN position and return its authoritative final stack."""

    def __init__(
        self,
        accounts: SQLAlchemyAccountRepository,
        ledger: SQLAlchemyLedgerRepository,
        positions: SQLAlchemyTablePositionRepository,
        operations: SQLAlchemyTableMoneyOperationRepository,
        balance_projection: AccountBalanceProjection,
        ledger_posting: LedgerPosting,
    ) -> None:
        """Store request-scoped collaborators."""
        self._accounts = accounts
        self._ledger = ledger
        self._positions = positions
        self._operations = operations
        self._balance_projection = balance_projection
        self._ledger_posting = ledger_posting

    async def execute(self, command: CashOutCommand) -> PlayerTablePositionModel:
        """Transfer a positive stack from pooled escrow or close a zero stack."""
        fingerprint = fingerprint_cash_out(command)
        operation_type = TableMoneyOperationType.CASH_OUT
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

        account_rows = await self._accounts.get_by_ids_for_update(
            {position.table_escrow_account_id, position.user_account_id},
        )
        accounts_by_id = index_accounts_by_id(account_rows)
        escrow = accounts_by_id.get(position.table_escrow_account_id)
        user_account = accounts_by_id.get(position.user_account_id)
        if escrow is None or user_account is None:
            raise TableMoneyDataIntegrityError()
        validate_position_escrow(position, escrow)
        validate_position_user_account(position, user_account)
        if escrow.status is AccountStatus.CLOSED:
            raise TableEscrowUnavailable()
        if user_account.status is AccountStatus.CLOSED:
            raise LedgerAccountUnavailable()

        ledger_transaction_id: UUID | None = None
        if command.amount_minor > 0:
            balances = await self._balance_projection.lock([escrow.id, user_account.id])
            if balances[escrow.id].posted_balance_minor < command.amount_minor:
                raise TableEscrowInsufficientBalance()

            draft = LedgerTransactionDraft(
                operation_id=command.operation_id,
                transaction_type=LedgerTransactionType.CASH_OUT,
                postings=(
                    Posting(account_id=escrow.id, amount_minor=-command.amount_minor),
                    Posting(account_id=user_account.id, amount_minor=command.amount_minor),
                ),
                reference_type=LedgerReferenceType.TABLE_POSITION,
                reference_id=position.id,
                description="Final table stack cashout",
            )
            posting_result = await self._ledger_posting.post(
                draft,
                position.asset_id,
                fingerprint,
                locked_balances=balances,
            )
            if posting_result is None:
                record = await self._ledger.get_by_operation_id(command.operation_id)
                if record is None:
                    raise TableMoneyWriteConflict()
                if record.payload_fingerprint != fingerprint:
                    raise IdempotencyConflict()
                raise TableMoneyDataIntegrityError()
            ledger_transaction_id = posting_result.transaction.id

        closed = await self._positions.save_closed(position.id, command.amount_minor)
        if closed is None:
            raise TableMoneyWriteConflict()
        await save_table_operation(
            operations=self._operations,
            operation_id=command.operation_id,
            position_id=position.id,
            operation_type=operation_type,
            payload_fingerprint=fingerprint,
            hold_id=None,
            ledger_transaction_id=ledger_transaction_id,
            amount_minor=command.amount_minor,
        )
        logfire.info(
            "Table CashOut completed",
            operation_id=str(command.operation_id),
            position_id=str(closed.id),
            table_id=str(closed.table_id),
            user_id=str(closed.user_id),
        )
        return closed
