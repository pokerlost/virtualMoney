"""Rake charge use case."""

from __future__ import annotations

import logfire

from application.accounts.services import AccountBalanceProjection, index_accounts_by_id
from application.errors import (
    IdempotencyConflict,
    RakeDataIntegrityError,
    RakeEscrowNotFound,
    RakeInsufficientEscrow,
    RakeWriteConflict,
    TableEscrowUnavailable,
)
from application.fingerprinting import fingerprint_charge_rake
from application.ledger import LedgerPosting
from application.rake.services import RakeAccountProvisioner
from domain.enums import (
    AccountStatus,
    AccountType,
    LedgerReferenceType,
    LedgerTransactionType,
    OwnerType,
)
from domain.ledger import LedgerTransactionDraft, Posting
from persistence.database.models import AccountModel, RakeOperationModel
from persistence.repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyLedgerRepository,
    SQLAlchemyRakeOperationRepository,
)

from .command import ChargeRakeCommand


def _validate_escrow(account: AccountModel, command: ChargeRakeCommand) -> None:
    if (
        account.account_type is not AccountType.TABLE_ESCROW
        or account.owner_type is not OwnerType.TABLE
        or account.owner_id != command.table_id
        or account.asset_id != command.asset_id
        or account.status is not AccountStatus.ACTIVE
    ):
        raise TableEscrowUnavailable()


class ChargeRakeHandler:
    """Transfer a trusted positive amount from table escrow to RAKE."""

    def __init__(
        self,
        accounts: SQLAlchemyAccountRepository,
        ledger: SQLAlchemyLedgerRepository,
        rake_operations: SQLAlchemyRakeOperationRepository,
        balance_projection: AccountBalanceProjection,
        ledger_posting: LedgerPosting,
        provisioner: RakeAccountProvisioner,
    ) -> None:
        """Store request-scoped collaborators."""
        self._accounts = accounts
        self._ledger = ledger
        self._rake_operations = rake_operations
        self._balance_projection = balance_projection
        self._ledger_posting = ledger_posting
        self._provisioner = provisioner

    async def _resolve_replay(
        self,
        operation: RakeOperationModel,
        fingerprint: str,
    ) -> RakeOperationModel:
        if operation.payload_fingerprint != fingerprint:
            raise IdempotencyConflict()
        record = await self._ledger.get_by_operation_id(operation.operation_id)
        if record is None:
            raise RakeDataIntegrityError()

        transaction = record
        expected_entries = [
            (operation.table_escrow_account_id, -operation.amount_minor),
            (operation.rake_account_id, operation.amount_minor),
        ]
        actual_entries = [(entry.account_id, entry.amount_minor) for entry in transaction.entries]
        if (
            transaction.id != operation.ledger_transaction_id
            or transaction.asset_id != operation.asset_id
            or transaction.transaction_type is not LedgerTransactionType.RAKE
            or transaction.reference_type != LedgerReferenceType.POKER_HAND
            or transaction.reference_id != operation.hand_id
            or record.payload_fingerprint != fingerprint
            or actual_entries != expected_entries
        ):
            raise RakeDataIntegrityError()
        return operation

    async def execute(self, command: ChargeRakeCommand) -> RakeOperationModel:
        """Post the transfer or return an exact idempotent replay."""
        fingerprint = fingerprint_charge_rake(command)
        replay = await self._rake_operations.get_by_operation_id(command.operation_id)
        if replay is not None:
            return await self._resolve_replay(replay, fingerprint)

        escrow = await self._accounts.get_table_escrow(
            command.table_id,
            command.asset_id,
        )
        if escrow is None:
            raise RakeEscrowNotFound()
        rake_account = await self._provisioner.get_or_create(command.asset_id)

        account_rows = await self._accounts.get_by_ids_for_update(
            {escrow.id, rake_account.id},
        )
        accounts_by_id = index_accounts_by_id(account_rows)
        locked_escrow = accounts_by_id.get(escrow.id)
        locked_rake = accounts_by_id.get(rake_account.id)
        if locked_escrow is None or locked_rake is None:
            raise RakeDataIntegrityError()
        _validate_escrow(locked_escrow, command)
        if (
            locked_rake.account_type is not AccountType.RAKE
            or locked_rake.owner_type is not OwnerType.SYSTEM
            or locked_rake.owner_id is not None
            or locked_rake.asset_id != command.asset_id
            or locked_rake.status is not AccountStatus.ACTIVE
        ):
            raise RakeDataIntegrityError()

        balances = await self._balance_projection.lock([locked_escrow.id, locked_rake.id])
        if balances[locked_escrow.id].posted_balance_minor < command.amount_minor:
            raise RakeInsufficientEscrow()

        posting_result = await self._ledger_posting.post(
            LedgerTransactionDraft(
                operation_id=command.operation_id,
                transaction_type=LedgerTransactionType.RAKE,
                postings=(
                    Posting(
                        account_id=locked_escrow.id,
                        amount_minor=-command.amount_minor,
                    ),
                    Posting(
                        account_id=locked_rake.id,
                        amount_minor=command.amount_minor,
                    ),
                ),
                reference_type=LedgerReferenceType.POKER_HAND,
                reference_id=command.hand_id,
                description="Poker Server rake charge",
            ),
            command.asset_id,
            fingerprint,
            locked_balances=balances,
        )
        if posting_result is None:
            concurrent = await self._rake_operations.get_by_operation_id(
                command.operation_id,
            )
            if concurrent is not None:
                return await self._resolve_replay(concurrent, fingerprint)
            record = await self._ledger.get_by_operation_id(command.operation_id)
            if record is not None:
                raise IdempotencyConflict()
            raise RakeWriteConflict()

        inserted = await self._rake_operations.insert_if_absent(
            operation_id=command.operation_id,
            table_id=command.table_id,
            hand_id=command.hand_id,
            asset_id=command.asset_id,
            table_escrow_account_id=locked_escrow.id,
            rake_account_id=locked_rake.id,
            amount_minor=command.amount_minor,
            ledger_transaction_id=posting_result.transaction.id,
            payload_fingerprint=fingerprint,
        )
        if not inserted:
            existing = await self._rake_operations.get_by_operation_id(
                command.operation_id,
            )
            if existing is not None and existing.payload_fingerprint != fingerprint:
                raise IdempotencyConflict()
            # Ledger and projection writes precede this audit. The conflict must
            # escape so the request-scoped transaction rolls them back.
            raise RakeWriteConflict()

        operation = await self._rake_operations.get_by_operation_id(command.operation_id)
        if operation is None:
            raise RakeDataIntegrityError()
        logfire.info(
            "Rake charged",
            ledger_transaction_id=str(operation.ledger_transaction_id),
            operation_id=str(operation.operation_id),
            table_id=str(operation.table_id),
        )
        return operation
