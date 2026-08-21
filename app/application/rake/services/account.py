"""Concurrency-safe RAKE account provisioning."""

from __future__ import annotations

from uuid import UUID

from application.errors import (
    AccountBalanceMissing,
    AssetNotFound,
    RakeAccountUnavailable,
)
from domain.enums import AccountStatus, AccountType, AssetStatus, OwnerType
from persistence.database.models import AccountModel
from persistence.repositories import (
    SQLAlchemyAccountBalanceRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyAssetRepository,
)


class RakeAccountProvisioner:
    """Get or create one system-owned RAKE account per asset."""

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
        if (
            account.account_type is not AccountType.RAKE
            or account.owner_type is not OwnerType.SYSTEM
            or account.owner_id is not None
            or account.status is not AccountStatus.ACTIVE
        ):
            raise RakeAccountUnavailable()
        if await self._balances.get_by_account_id(account.id) is None:
            raise AccountBalanceMissing()
        return account

    async def get_or_create(self, asset_id: UUID) -> AccountModel:
        """Resolve one logical rake account inside the request transaction."""
        asset = await self._assets.get_by_id(asset_id)
        if asset is None:
            raise AssetNotFound()
        if asset.status is not AssetStatus.ACTIVE:
            raise RakeAccountUnavailable()

        existing = await self._accounts.get_rake_account(asset_id)
        if existing is not None:
            return await self._validate_existing(existing)

        inserted = await self._accounts.insert_if_absent(
            account_id=None,
            asset_id=asset_id,
            account_type=AccountType.RAKE,
            owner_type=OwnerType.SYSTEM,
            owner_id=None,
            status=AccountStatus.ACTIVE,
        )
        if inserted is None:
            concurrent = await self._accounts.get_rake_account(asset_id)
            if concurrent is None:
                raise RakeAccountUnavailable()
            return await self._validate_existing(concurrent)

        await self._balances.insert_zero(inserted.id)
        return inserted
