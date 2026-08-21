"""Account creation use case."""

from __future__ import annotations

import logfire

from application.errors import (
    AccountBalanceMissing,
    AccountCreationConflict,
    AssetNotFound,
)
from persistence.database.models import AccountModel
from persistence.repositories import (
    SQLAlchemyAccountBalanceRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyAssetRepository,
)

from .command import CreateAccountCommand


def _account_matches_command(account: AccountModel, command: CreateAccountCommand) -> bool:
    return (
        account.id == command.account_id
        and account.asset_id == command.asset_id
        and account.account_type is command.account_type
        and account.owner_type is command.owner_type
        and account.owner_id == command.owner_id
        and account.status is command.status
    )


class CreateAccountHandler:
    """Create an account and its zero projection atomically."""

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

    async def _resolve_replay(
        self,
        account: AccountModel,
        command: CreateAccountCommand,
    ) -> AccountModel:
        if not _account_matches_command(account, command):
            raise AccountCreationConflict()
        if await self._balances.get_by_account_id(account.id) is None:
            raise AccountBalanceMissing()
        return account

    async def execute(self, command: CreateAccountCommand) -> AccountModel:
        """Create an account or return its exact stable-identity replay."""
        existing = await self._accounts.get_by_id(command.account_id)
        if existing is not None:
            return await self._resolve_replay(existing, command)

        if await self._assets.get_by_id_for_update(command.asset_id) is None:
            raise AssetNotFound()
        inserted = await self._accounts.insert_if_absent(
            account_id=command.account_id,
            asset_id=command.asset_id,
            account_type=command.account_type,
            owner_type=command.owner_type,
            owner_id=command.owner_id,
            status=command.status,
        )
        if inserted is None:
            concurrent = await self._accounts.get_by_id(command.account_id)
            if concurrent is None:
                raise AccountCreationConflict()
            return await self._resolve_replay(concurrent, command)

        await self._balances.insert_zero(inserted.id)
        logfire.info(
            "AccountModel and zero balance projection created",
            account_id=str(inserted.id),
            asset_id=str(inserted.asset_id),
        )
        return inserted
