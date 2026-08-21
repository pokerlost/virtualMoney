"""SQLAlchemy immutable refund operation repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from persistence.database.models import RefundOperationModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyRefundOperationRepository(SQLAlchemyEntityRepository[RefundOperationModel]):
    """Append full-compensation audits without committing."""

    model = RefundOperationModel

    async def get_by_operation_id(self, operation_id: UUID) -> RefundOperationModel | None:
        """Return one immutable refund audit by its operation ID."""
        result = await self._read_scalar(
            select(RefundOperationModel).where(
                RefundOperationModel.operation_id == operation_id,
            ),
        )
        return result.one_or_none()

    async def get_by_target_operation_id(
        self,
        target_operation_id: UUID,
    ) -> RefundOperationModel | None:
        """Return the unique refund of a target business operation."""
        result = await self._read_scalar(
            select(RefundOperationModel).where(
                RefundOperationModel.target_operation_id == target_operation_id,
            ),
        )
        return result.one_or_none()

    async def insert_if_absent(
        self,
        *,
        operation_id: UUID,
        target_operation_id: UUID,
        original_ledger_transaction_id: UUID,
        reversal_ledger_transaction_id: UUID,
        reason: str,
        payload_fingerprint: str,
    ) -> bool:
        """Append a refund audit unless a unique refund identity conflicts."""
        result = await self._read_scalar(
            insert(RefundOperationModel)
            .values(
                operation_id=operation_id,
                target_operation_id=target_operation_id,
                original_ledger_transaction_id=original_ledger_transaction_id,
                reversal_ledger_transaction_id=reversal_ledger_transaction_id,
                reason=reason,
                payload_fingerprint=payload_fingerprint,
            )
            .on_conflict_do_nothing()
            .returning(RefundOperationModel.id),
        )
        return result.one_or_none() is not None
