"""Command for idempotent account creation."""

from __future__ import annotations

from typing import Self

from pydantic import model_validator

from domain import ValueModel
from domain.account_validation import validate_account_metadata
from domain.enums import AccountStatus, AccountType, OwnerType
from domain.types import NonNilUUID


class CreateAccountCommand(ValueModel):
    """Stable account identity and metadata for atomic creation."""

    account_id: NonNilUUID
    asset_id: NonNilUUID
    account_type: AccountType
    owner_type: OwnerType
    owner_id: NonNilUUID | None
    status: AccountStatus = AccountStatus.ACTIVE

    @model_validator(mode="after")
    def validate_ownership(self) -> Self:
        """Validate the account purpose and owner namespace."""
        validate_account_metadata(
            account_type=self.account_type,
            owner_type=self.owner_type,
            owner_id=self.owner_id,
        )
        return self
