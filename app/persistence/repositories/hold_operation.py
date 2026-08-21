"""SQLAlchemy immutable hold operation repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from domain.enums import HoldOperationType
from persistence.database.models import HoldOperationModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyHoldOperationRepository(SQLAlchemyEntityRepository[HoldOperationModel]):
    """Append hold audits without owning transaction completion."""

    model = HoldOperationModel

    async def get_by_operation_id(self, operation_id: UUID) -> HoldOperationModel | None:
        """Return one immutable hold audit by idempotency key."""
        result = await self._read_scalar(
            select(HoldOperationModel).where(
                HoldOperationModel.operation_id == operation_id,
            ),
        )
        return result.one_or_none()

    async def insert_if_absent(
        self,
        operation_id: UUID,
        hold_id: UUID,
        operation_type: HoldOperationType,
        payload_fingerprint: str,
        ledger_transaction_id: UUID | None,
    ) -> bool:
        """Append a hold audit unless its unique identity already exists."""
        result = await self._read_scalar(
            insert(HoldOperationModel)
            .values(
                operation_id=operation_id,
                hold_id=hold_id,
                operation_type=operation_type,
                payload_fingerprint=payload_fingerprint,
                ledger_transaction_id=ledger_transaction_id,
            )
            .on_conflict_do_nothing()
            .returning(HoldOperationModel.id),
        )
        return result.one_or_none() is not None
