"""Concurrency-safe TABLE_ESCROW account provisioning."""

from __future__ import annotations

from uuid import UUID

from application.errors import (
    AccountBalanceMissing,
    AssetNotFound,
    TableEscrowUnavailable,
)
from domain.enums import AccountStatus, AccountType, AssetStatus, OwnerType
from persistence.database.models import AccountModel
from persistence.repositories import (
    SQLAlchemyAccountBalanceRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyAssetRepository,
)


class TableEscrowProvisioner:
    """Get or create one table-owned account with a zero projection."""

    def __init__(
        self,
        accounts: SQLAlchemyAccountRepository,
        assets: SQLAlchemyAssetRepository,
        balances: SQLAlchemyAccountBalanceRepository,
    ) -> None:
        """Store request-scoped collaborators."""
        self._accounts = accounts
        self._assets = assets
        self._balances = balances

    async def _validate_existing(self, account: AccountModel) -> AccountModel:
        if account.status is AccountStatus.CLOSED:
            raise TableEscrowUnavailable()
        if await self._balances.get_by_account_id(account.id) is None:
            raise AccountBalanceMissing()
        return account

    async def get_or_create(self, *, table_id: UUID, asset_id: UUID) -> AccountModel:
        """Resolve one logical table/asset escrow inside the request transaction."""
        existing = await self._accounts.get_table_escrow(table_id, asset_id)
        asset = await self._assets.get_by_id(asset_id)
        if asset is None:
            raise AssetNotFound()
        if asset.status is not AssetStatus.ACTIVE:
            raise TableEscrowUnavailable()
        if existing is not None:
            return await self._validate_existing(existing)

        inserted = await self._accounts.insert_if_absent(
            account_id=None,
            asset_id=asset_id,
            account_type=AccountType.TABLE_ESCROW,
            owner_type=OwnerType.TABLE,
            owner_id=table_id,
            status=AccountStatus.ACTIVE,
        )
        if inserted is None:
            concurrent = await self._accounts.get_table_escrow(table_id, asset_id)
            if concurrent is None:
                raise TableEscrowUnavailable()
            return await self._validate_existing(concurrent)

        await self._balances.insert_zero(inserted.id)
        return inserted
