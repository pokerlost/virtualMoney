"""SQLAlchemy durable table-position repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert

from domain.enums import PlayerTablePositionStatus
from persistence.database.models import PlayerTablePositionModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyTablePositionRepository(
    SQLAlchemyEntityRepository[PlayerTablePositionModel],
):
    """Persist serialized OPEN/CLOSED table-position transitions."""

    model = PlayerTablePositionModel

    async def get_by_id_for_update(
        self,
        position_id: UUID,
    ) -> PlayerTablePositionModel | None:
        """Lock one durable position for a serialized lifecycle transition."""
        result = await self._read_scalar(
            select(PlayerTablePositionModel)
            .where(PlayerTablePositionModel.id == position_id)
            .with_for_update(),
        )
        return result.one_or_none()

    async def get_open(
        self,
        user_id: UUID,
        table_id: UUID,
        asset_id: UUID,
    ) -> PlayerTablePositionModel | None:
        """Return the unique open position for one user, table, and asset."""
        result = await self._read_scalar(
            select(PlayerTablePositionModel).where(
                PlayerTablePositionModel.user_id == user_id,
                PlayerTablePositionModel.table_id == table_id,
                PlayerTablePositionModel.asset_id == asset_id,
                PlayerTablePositionModel.status == PlayerTablePositionStatus.OPEN,
            ),
        )
        return result.one_or_none()

    async def try_add_open(
        self,
        *,
        user_id: UUID,
        table_id: UUID,
        asset_id: UUID,
        user_account_id: UUID,
        table_escrow_account_id: UUID,
        total_buy_in_minor: int,
    ) -> PlayerTablePositionModel | None:
        """Insert an open position when the active-position key is unclaimed."""
        result = await self._read_scalar(
            insert(PlayerTablePositionModel)
            .values(
                user_id=user_id,
                table_id=table_id,
                asset_id=asset_id,
                user_account_id=user_account_id,
                table_escrow_account_id=table_escrow_account_id,
                status=PlayerTablePositionStatus.OPEN,
                total_buy_in_minor=total_buy_in_minor,
                total_cash_out_minor=0,
                closed_at=None,
            )
            .on_conflict_do_nothing()
            .returning(PlayerTablePositionModel),
        )
        return result.one_or_none()

    async def save_rebuy_total(
        self,
        position_id: UUID,
        total_buy_in_minor: int,
    ) -> PlayerTablePositionModel | None:
        """Replace the aggregate buy-in total while the position remains open."""
        result = await self._read_scalar(
            update(PlayerTablePositionModel)
            .where(
                PlayerTablePositionModel.id == position_id,
                PlayerTablePositionModel.status == PlayerTablePositionStatus.OPEN,
            )
            .values(
                total_buy_in_minor=total_buy_in_minor,
                updated_at=func.transaction_timestamp(),
            )
            .returning(PlayerTablePositionModel),
        )
        return result.one_or_none()

    async def save_closed(
        self,
        position_id: UUID,
        total_cash_out_minor: int,
    ) -> PlayerTablePositionModel | None:
        """Close an open position with its authoritative final stack."""
        timestamp = func.transaction_timestamp()
        result = await self._read_scalar(
            update(PlayerTablePositionModel)
            .where(
                PlayerTablePositionModel.id == position_id,
                PlayerTablePositionModel.status == PlayerTablePositionStatus.OPEN,
            )
            .values(
                status=PlayerTablePositionStatus.CLOSED,
                total_cash_out_minor=total_cash_out_minor,
                updated_at=timestamp,
                closed_at=timestamp,
            )
            .returning(PlayerTablePositionModel),
        )
        return result.one_or_none()
