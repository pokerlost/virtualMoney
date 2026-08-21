"""Validation shared by table-position operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from application.errors import (
    BuyInHoldInvalid,
    PositionAssetMismatch,
    PositionOwnershipMismatch,
    TableEscrowUnavailable,
)
from domain.enums import AccountStatus, AccountType, OwnerType
from persistence.database.models import AccountModel, PlayerTablePositionModel

if TYPE_CHECKING:
    from application.table_positions.buy_in import BuyInCommand


def validate_buy_in_source(account: AccountModel, command: BuyInCommand) -> None:
    """Validate the USER account funding an initial BuyIn."""
    if account.account_type is not AccountType.USER or account.owner_type is not OwnerType.USER:
        raise BuyInHoldInvalid()
    if account.owner_id != command.user_id:
        raise PositionOwnershipMismatch()
    if account.status is AccountStatus.CLOSED:
        raise BuyInHoldInvalid()


def validate_position_user_account(
    position: PlayerTablePositionModel,
    account: AccountModel,
) -> None:
    """Validate the user-side account linked by a position."""
    if (
        account.id != position.user_account_id
        or account.account_type is not AccountType.USER
        or account.owner_type is not OwnerType.USER
        or account.owner_id != position.user_id
    ):
        raise PositionOwnershipMismatch()
    if account.asset_id != position.asset_id:
        raise PositionAssetMismatch()


def validate_position_escrow(
    position: PlayerTablePositionModel,
    account: AccountModel,
) -> None:
    """Validate the TABLE_ESCROW account linked by a position."""
    if (
        account.id != position.table_escrow_account_id
        or account.account_type is not AccountType.TABLE_ESCROW
        or account.owner_type is not OwnerType.TABLE
        or account.owner_id != position.table_id
    ):
        raise TableEscrowUnavailable()
    if account.asset_id != position.asset_id:
        raise PositionAssetMismatch()
