"""SQLAlchemy account balance entity repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, insert, select, update

from persistence.database.models import AccountBalanceModel

from .base import SQLAlchemyRepository


class SQLAlchemyAccountBalanceRepository(SQLAlchemyRepository):
    """Read and update persisted account balances without completing transactions."""

    async def get_by_account_id(self, account_id: UUID) -> AccountBalanceModel | None:
        """Return the current projection for one account."""
        result = await self._read_scalar(
            select(AccountBalanceModel).where(
                AccountBalanceModel.account_id == account_id,
            ),
        )
        return result.one_or_none()

    async def get_many_for_update(
        self,
        account_ids: list[UUID],
    ) -> list[AccountBalanceModel]:
        """Lock balance rows in deterministic UUID order."""
        ordered_ids = sorted(set(account_ids), key=lambda account_id: account_id.int)
        if not ordered_ids:
            return []
        result = await self._read_scalar(
            select(AccountBalanceModel)
            .where(AccountBalanceModel.account_id.in_(ordered_ids))
            .order_by(AccountBalanceModel.account_id)
            .with_for_update(),
        )
        return result.all()

    async def insert_zero(self, account_id: UUID) -> AccountBalanceModel:
        """Insert and return a zero balance projection in one statement."""
        result = await self._read_scalar(
            insert(AccountBalanceModel)
            .values(
                account_id=account_id,
                posted_balance_minor=0,
                held_balance_minor=0,
                version=0,
            )
            .returning(AccountBalanceModel),
        )
        return result.one()

    async def apply_update(
        self,
        account_id: UUID,
        posted_balance_minor: int,
        held_balance_minor: int,
    ) -> bool:
        """Replace locked totals and increment the projection version."""
        result = await self._read_scalar(
            update(AccountBalanceModel)
            .where(AccountBalanceModel.account_id == account_id)
            .values(
                posted_balance_minor=posted_balance_minor,
                held_balance_minor=held_balance_minor,
                version=AccountBalanceModel.version + 1,
                updated_at=func.now(),
            )
            .returning(AccountBalanceModel.account_id),
        )
        return result.one_or_none() is not None
