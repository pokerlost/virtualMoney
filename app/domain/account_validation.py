"""Private account ownership validation."""

from __future__ import annotations

from uuid import UUID

from .enums import AccountType, OwnerType
from .errors import DomainValidationError, InvalidAccountOwnership


def expected_owner_type(account_type: AccountType) -> OwnerType:
    """Return the only owner namespace valid for an account purpose."""
    match account_type:
        case AccountType.USER:
            return OwnerType.USER
        case AccountType.TABLE_ESCROW:
            return OwnerType.TABLE
        case AccountType.TREASURY | AccountType.RAKE:
            return OwnerType.SYSTEM
    raise DomainValidationError("account type is not supported")


def validate_account_metadata(
    *,
    account_type: AccountType,
    owner_type: OwnerType,
    owner_id: UUID | None,
) -> None:
    """Validate strict ownership semantics for an account."""
    if owner_type is not expected_owner_type(account_type):
        raise InvalidAccountOwnership()
    if (owner_type is OwnerType.SYSTEM) != (owner_id is None):
        raise InvalidAccountOwnership()
