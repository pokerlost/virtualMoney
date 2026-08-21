"""SQLAlchemy account repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from domain.enums import AccountStatus, AccountType, OwnerType
from persistence.database.models import AccountModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyAccountRepository(SQLAlchemyEntityRepository[AccountModel]):
    """Persist accounts through one injected request session."""

    model = AccountModel

    async def insert_if_absent(
        self,
        *,
        account_id: UUID | None,
        asset_id: UUID,
        account_type: AccountType,
        owner_type: OwnerType,
        owner_id: UUID | None,
        status: AccountStatus,
    ) -> AccountModel | None:
        """Insert one account and return the row from the same statement."""
        statement = (
            insert(AccountModel)
            .values(
                asset_id=asset_id,
                account_type=account_type,
                owner_type=owner_type,
                owner_id=owner_id,
                status=status,
            )
            .on_conflict_do_nothing()
            .returning(AccountModel)
        )
        if account_id is not None:
            statement = statement.values(id=account_id)
        result = await self._read_scalar(statement)
        return result.one_or_none()

    async def get_table_escrow(self, table_id: UUID, asset_id: UUID) -> AccountModel | None:
        """Return the pooled escrow account for one table and asset."""
        result = await self._read_scalar(
            select(AccountModel).where(
                AccountModel.owner_type == OwnerType.TABLE,
                AccountModel.owner_id == table_id,
                AccountModel.asset_id == asset_id,
                AccountModel.account_type == AccountType.TABLE_ESCROW,
            ),
        )
        return result.one_or_none()

    async def get_rake_account(self, asset_id: UUID) -> AccountModel | None:
        """Return the unique system rake account for an asset."""
        result = await self._read_scalar(
            select(AccountModel).where(
                AccountModel.owner_type == OwnerType.SYSTEM,
                AccountModel.owner_id.is_(None),
                AccountModel.asset_id == asset_id,
                AccountModel.account_type == AccountType.RAKE,
            ),
        )
        return result.one_or_none()

    async def get_by_ids_for_update(
        self,
        account_ids: set[UUID],
    ) -> list[AccountModel]:
        """Lock and return accounts in deterministic UUID order."""
        if not account_ids:
            return []
        ordered_ids = sorted(account_ids, key=lambda account_id: account_id.int)
        result = await self._read_scalar(
            select(AccountModel)
            .where(AccountModel.id.in_(ordered_ids))
            .order_by(AccountModel.id)
            .with_for_update(),
        )
        return result.all()
