"""SQLAlchemy hold repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert

from domain.enums import HoldStatus
from persistence.database.models import HoldModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyHoldRepository(SQLAlchemyEntityRepository[HoldModel]):
    """Persist explicit hold lifecycle transitions without committing."""

    model = HoldModel

    async def get_by_id_for_update(self, hold_id: UUID) -> HoldModel | None:
        """Lock one hold for a serialized lifecycle transition."""
        result = await self._read_scalar(
            select(HoldModel).where(HoldModel.id == hold_id).with_for_update(),
        )
        return result.one_or_none()

    async def create_hold(
        self,
        account_id: UUID,
        amount_minor: int,
        reference_type: str | None,
        reference_id: UUID | None,
    ) -> HoldModel:
        """Insert an active hold and return its server-generated state."""
        result = await self._read_scalar(
            insert(HoldModel)
            .values(
                account_id=account_id,
                amount_minor=amount_minor,
                status=HoldStatus.ACTIVE,
                reference_type=reference_type,
                reference_id=reference_id,
                released_at=None,
                captured_at=None,
                capture_ledger_transaction_id=None,
            )
            .returning(HoldModel),
        )
        return result.one()

    async def save_released(self, hold_id: UUID) -> HoldModel | None:
        """Transition one active hold to released when it still matches."""
        timestamp = func.transaction_timestamp()
        result = await self._read_scalar(
            update(HoldModel)
            .where(HoldModel.id == hold_id, HoldModel.status == HoldStatus.ACTIVE)
            .values(
                status=HoldStatus.RELEASED,
                updated_at=timestamp,
                released_at=timestamp,
            )
            .returning(HoldModel),
        )
        return result.one_or_none()

    async def save_captured(
        self,
        hold_id: UUID,
        ledger_transaction_id: UUID,
    ) -> HoldModel | None:
        """Transition one active hold to captured and link its ledger row."""
        timestamp = func.transaction_timestamp()
        result = await self._read_scalar(
            update(HoldModel)
            .where(HoldModel.id == hold_id, HoldModel.status == HoldStatus.ACTIVE)
            .values(
                status=HoldStatus.CAPTURED,
                updated_at=timestamp,
                captured_at=timestamp,
                capture_ledger_transaction_id=ledger_transaction_id,
            )
            .returning(HoldModel),
        )
        return result.one_or_none()

    async def calculate_active_held_balance(self, account_id: UUID) -> int:
        """Sum active holds for reconciliation of one account."""
        result = await self._read_scalar(
            select(func.coalesce(func.sum(HoldModel.amount_minor), 0)).where(
                HoldModel.account_id == account_id,
                HoldModel.status == HoldStatus.ACTIVE,
            ),
        )
        return result.one()
