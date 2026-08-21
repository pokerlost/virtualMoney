"""Full immutable financial compensation use case."""

from __future__ import annotations

from uuid import UUID

import logfire

from application.errors import (
    FinancialOperationNotFound,
    FinancialOperationNotRefundable,
    IdempotencyConflict,
    LedgerTransactionAlreadyReversed,
    RefundAlreadyCompleted,
    RefundDataIntegrityError,
    RefundWriteConflict,
)
from application.fingerprinting import fingerprint_refund_operation
from application.ledger import LedgerReversal, ReverseLedgerTransactionCommand
from domain.enums import LedgerReferenceType, LedgerTransactionType
from persistence.database.models import RefundOperationModel
from persistence.repositories import (
    SQLAlchemyHoldOperationRepository,
    SQLAlchemyLedgerRepository,
    SQLAlchemyRefundOperationRepository,
    SQLAlchemyTableMoneyOperationRepository,
)

from .command import RefundFinancialOperationCommand


class RefundOperationHandler:
    """Compensate one complete ledger-backed financial operation."""

    def __init__(
        self,
        ledger: SQLAlchemyLedgerRepository,
        hold_operations: SQLAlchemyHoldOperationRepository,
        table_operations: SQLAlchemyTableMoneyOperationRepository,
        refund_operations: SQLAlchemyRefundOperationRepository,
        ledger_reversal: LedgerReversal,
    ) -> None:
        """Store request-scoped collaborators."""
        self._ledger = ledger
        self._hold_operations = hold_operations
        self._table_operations = table_operations
        self._refund_operations = refund_operations
        self._ledger_reversal = ledger_reversal

    async def _resolve_replay(
        self,
        operation: RefundOperationModel,
        command: RefundFinancialOperationCommand,
        fingerprint: str,
    ) -> RefundOperationModel:
        if (
            operation.target_operation_id != command.target_operation_id
            or operation.payload_fingerprint != fingerprint
        ):
            raise IdempotencyConflict()

        target = await self._ledger.get_by_operation_id(operation.target_operation_id)
        reversal = await self._ledger.get_by_operation_id(operation.operation_id)
        if target is None or reversal is None:
            raise RefundDataIntegrityError()
        original_transaction = target
        reversal_transaction = reversal
        if (
            original_transaction.id != operation.original_ledger_transaction_id
            or reversal_transaction.id != operation.reversal_ledger_transaction_id
            or reversal_transaction.asset_id != original_transaction.asset_id
            or reversal_transaction.transaction_type is not LedgerTransactionType.REVERSAL
            or reversal_transaction.reversal_of_transaction_id
            != operation.original_ledger_transaction_id
            or reversal_transaction.reference_type != LedgerReferenceType.FINANCIAL_REFUND
            or reversal_transaction.reference_id != operation.target_operation_id
        ):
            raise RefundDataIntegrityError()
        return operation

    async def _known_non_refundable_operation(self, operation_id: UUID) -> bool:
        if await self._table_operations.get_by_operation_id(operation_id) is not None:
            return True
        if await self._hold_operations.get_by_operation_id(operation_id) is not None:
            return True
        return await self._ledger.get_by_operation_id(operation_id) is not None

    async def execute(
        self,
        command: RefundFinancialOperationCommand,
    ) -> RefundOperationModel:
        """Append a complete reversal and refund audit without rewriting history."""
        fingerprint = fingerprint_refund_operation(command)
        replay = await self._refund_operations.get_by_operation_id(command.operation_id)
        if replay is not None:
            return await self._resolve_replay(replay, command, fingerprint)

        target = await self._ledger.get_by_operation_id(command.target_operation_id)
        if target is None:
            if await self._known_non_refundable_operation(command.target_operation_id):
                raise FinancialOperationNotRefundable()
            raise FinancialOperationNotFound()

        existing_refund = await self._refund_operations.get_by_target_operation_id(
            command.target_operation_id,
        )
        if existing_refund is not None:
            raise RefundAlreadyCompleted()

        reversal_command = ReverseLedgerTransactionCommand(
            operation_id=command.operation_id,
            transaction_id=target.id,
            reference_type=LedgerReferenceType.FINANCIAL_REFUND,
            reference_id=command.target_operation_id,
            description=command.reason,
        )
        try:
            reversal = await self._ledger_reversal.reverse(reversal_command)
        except LedgerTransactionAlreadyReversed as exception:
            concurrent_refund = await self._refund_operations.get_by_target_operation_id(
                command.target_operation_id,
            )
            if concurrent_refund is not None:
                raise RefundAlreadyCompleted() from exception
            raise

        if reversal.idempotent_replay:
            concurrent = await self._refund_operations.get_by_operation_id(
                command.operation_id,
            )
            if concurrent is not None:
                return await self._resolve_replay(concurrent, command, fingerprint)
            raise RefundDataIntegrityError()

        inserted = await self._refund_operations.insert_if_absent(
            operation_id=command.operation_id,
            target_operation_id=command.target_operation_id,
            original_ledger_transaction_id=target.id,
            reversal_ledger_transaction_id=reversal.transaction.id,
            reason=command.reason,
            payload_fingerprint=fingerprint,
        )
        if not inserted:
            existing = await self._refund_operations.get_by_operation_id(
                command.operation_id,
            )
            if existing is not None and (
                existing.target_operation_id != command.target_operation_id
                or existing.payload_fingerprint != fingerprint
            ):
                raise IdempotencyConflict()
            if (
                await self._refund_operations.get_by_target_operation_id(
                    command.target_operation_id,
                )
                is not None
            ):
                raise RefundAlreadyCompleted()
            # The reversal was inserted before the audit conflict. Raising ensures
            # the request transaction rolls the reversal and projection back.
            raise RefundWriteConflict()

        operation = await self._refund_operations.get_by_operation_id(command.operation_id)
        if operation is None:
            raise RefundDataIntegrityError()
        logfire.info(
            "Financial operation compensated",
            ledger_transaction_id=str(operation.reversal_ledger_transaction_id),
            operation_id=str(operation.operation_id),
            target_operation_id=str(operation.target_operation_id),
        )
        return operation
