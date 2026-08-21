"""Shared validation for accounts participating in ledger postings."""

from __future__ import annotations

from uuid import UUID

from application.errors import (
    LedgerAccountNotFound,
    LedgerAccountUnavailable,
    LedgerAssetMismatch,
)
from domain.enums import AccountStatus
from domain.ledger import Posting
from persistence.database.models import AccountModel


def validate_ledger_accounts(
    postings: tuple[Posting, ...],
    accounts: dict[UUID, AccountModel],
    *,
    allow_frozen: bool,
) -> UUID:
    """Validate completeness, one asset, and permitted account states."""
    expected_account_ids = {posting.account_id for posting in postings}
    if set(accounts) != expected_account_ids:
        raise LedgerAccountNotFound()

    asset_ids = {account.asset_id for account in accounts.values()}
    if len(asset_ids) != 1:
        raise LedgerAssetMismatch()

    for account in accounts.values():
        if account.status is AccountStatus.CLOSED:
            raise LedgerAccountUnavailable()
        if account.status is AccountStatus.FROZEN and not allow_frozen:
            raise LedgerAccountUnavailable()
    return asset_ids.pop()
