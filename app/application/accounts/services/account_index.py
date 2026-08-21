"""Application-side account collection indexing."""

from __future__ import annotations

from uuid import UUID

from persistence.database.models import AccountModel


def index_accounts_by_id(accounts: list[AccountModel]) -> dict[UUID, AccountModel]:
    """Index fetched accounts for business validation and lookup."""
    return {account.id: account for account in accounts}
