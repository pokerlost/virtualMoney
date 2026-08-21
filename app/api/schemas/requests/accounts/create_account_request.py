"""Account creation request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.accounts import CreateAccountCommand
from domain.enums import AccountStatus, AccountType, OwnerType
from domain.types import NonNilUUID


class CreateAccountRequest(RequestModel):
    """Accept stable account identity and ownership metadata."""

    account_id: NonNilUUID = Field(description="Stable service-owned account UUID.")
    asset_id: NonNilUUID = Field(description="Authoritative internal asset UUID.")
    account_type: AccountType = Field(description="Accounting purpose of the account.")
    owner_type: OwnerType = Field(description="Namespace of the opaque owner UUID.")
    owner_id: NonNilUUID | None = Field(
        description="Opaque owner UUID, or null exactly when ownerType is SYSTEM.",
    )
    status: AccountStatus = Field(
        default=AccountStatus.ACTIVE,
        description="Initial account availability state.",
    )

    def to_command(self) -> CreateAccountCommand:
        """Map the request to an application command."""
        return CreateAccountCommand(
            account_id=self.account_id,
            asset_id=self.asset_id,
            account_type=self.account_type,
            owner_type=self.owner_type,
            owner_id=self.owner_id,
            status=self.status,
        )
