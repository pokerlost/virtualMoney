"""Table-money idempotency and immutable audit helpers."""

from __future__ import annotations

from uuid import UUID

from application.errors import (
    IdempotencyConflict,
    TableMoneyDataIntegrityError,
    TableMoneyWriteConflict,
)
from domain.enums import PlayerTablePositionStatus, TableMoneyOperationType
from persistence.database.models import PlayerTablePositionModel, TableMoneyOperationModel
from persistence.repositories import (
    SQLAlchemyTableMoneyOperationRepository,
    SQLAlchemyTablePositionRepository,
)


async def _resolve_operation_replay(
    operation: TableMoneyOperationModel,
    *,
    expected_type: TableMoneyOperationType,
    expected_fingerprint: str,
    positions: SQLAlchemyTablePositionRepository,
) -> PlayerTablePositionModel:
    if (
        operation.operation_type is not expected_type
        or operation.payload_fingerprint != expected_fingerprint
    ):
        raise IdempotencyConflict()

    position = await positions.get_by_id(operation.position_id)
    if position is None:
        raise TableMoneyDataIntegrityError()
    if expected_type is TableMoneyOperationType.CASH_OUT and (
        position.status is not PlayerTablePositionStatus.CLOSED
        or position.total_cash_out_minor != operation.amount_minor
    ):
        raise TableMoneyDataIntegrityError()
    return position


async def find_table_operation_replay(
    operation_id: UUID,
    *,
    expected_type: TableMoneyOperationType,
    expected_fingerprint: str,
    operations: SQLAlchemyTableMoneyOperationRepository,
    positions: SQLAlchemyTablePositionRepository,
) -> PlayerTablePositionModel | None:
    """Return a validated replay when the operation already exists."""
    operation = await operations.get_by_operation_id(operation_id)
    if operation is None:
        return None
    return await _resolve_operation_replay(
        operation,
        expected_type=expected_type,
        expected_fingerprint=expected_fingerprint,
        positions=positions,
    )


async def save_table_operation(
    *,
    operations: SQLAlchemyTableMoneyOperationRepository,
    operation_id: UUID,
    position_id: UUID,
    operation_type: TableMoneyOperationType,
    payload_fingerprint: str,
    hold_id: UUID | None,
    ledger_transaction_id: UUID | None,
    amount_minor: int,
) -> None:
    """Append an audit or force rollback after a concurrent audit conflict."""
    inserted = await operations.insert_if_absent(
        operation_id=operation_id,
        position_id=position_id,
        operation_type=operation_type,
        payload_fingerprint=payload_fingerprint,
        hold_id=hold_id,
        ledger_transaction_id=ledger_transaction_id,
        amount_minor=amount_minor,
    )
    if inserted:
        return

    existing = await operations.get_by_operation_id(operation_id)
    if existing is not None and (
        existing.operation_type is not operation_type
        or existing.payload_fingerprint != payload_fingerprint
    ):
        raise IdempotencyConflict()
    # Callers append this audit after economic writes. A typed conflict exits the
    # external request transaction and prevents those intermediate writes committing.
    raise TableMoneyWriteConflict()
