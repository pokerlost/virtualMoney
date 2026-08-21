"""Idempotent hold operation replay resolution."""

from __future__ import annotations

from uuid import UUID

from application.errors import HoldDataIntegrityError, IdempotencyConflict
from domain.enums import HoldOperationType, HoldStatus
from persistence.database.models import HoldModel, HoldOperationModel
from persistence.repositories import SQLAlchemyHoldOperationRepository, SQLAlchemyHoldRepository


async def resolve_hold_replay(
    operation: HoldOperationModel,
    *,
    expected_type: HoldOperationType,
    expected_fingerprint: str,
    holds: SQLAlchemyHoldRepository,
) -> HoldModel:
    """Validate one immutable operation and load its terminal hold state."""
    if (
        operation.operation_type is not expected_type
        or operation.payload_fingerprint != expected_fingerprint
    ):
        raise IdempotencyConflict()

    hold = await holds.get_by_id(operation.hold_id)
    if hold is None:
        raise HoldDataIntegrityError()
    if expected_type is HoldOperationType.RELEASE and hold.status is not HoldStatus.RELEASED:
        raise HoldDataIntegrityError()
    if expected_type is HoldOperationType.CAPTURE and (
        hold.status is not HoldStatus.CAPTURED
        or hold.capture_ledger_transaction_id != operation.ledger_transaction_id
    ):
        raise HoldDataIntegrityError()
    return hold


async def find_hold_replay(
    operation_id: UUID,
    *,
    expected_type: HoldOperationType,
    expected_fingerprint: str,
    operations: SQLAlchemyHoldOperationRepository,
    holds: SQLAlchemyHoldRepository,
) -> HoldModel | None:
    """Return a validated replay when the operation ID already exists."""
    operation = await operations.get_by_operation_id(operation_id)
    if operation is None:
        return None
    return await resolve_hold_replay(
        operation,
        expected_type=expected_type,
        expected_fingerprint=expected_fingerprint,
        holds=holds,
    )
