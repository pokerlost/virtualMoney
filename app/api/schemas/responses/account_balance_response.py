"""Public account balance projection response."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import ResponseModel
from domain.money import POSTGRES_BIGINT_MAX
from domain.types import (
    NonNegativeMoneyMinor,
    NonNilUUID,
    SignedMoneyMinor,
    UtcDatetime,
)


class AccountBalanceResponse(ResponseModel):
    """Expose posted, held, and derived available funds."""

    account_id: NonNilUUID
    asset_id: NonNilUUID
    posted_balance_minor: SignedMoneyMinor = Field(
        description="Sum of immutable posted ledger entries.",
    )
    held_balance_minor: NonNegativeMoneyMinor = Field(
        description="Sum of ACTIVE holds.",
    )
    available_balance_minor: SignedMoneyMinor = Field(
        description="Derived postedBalanceMinor minus heldBalanceMinor.",
    )
    version: int = Field(
        strict=True,
        ge=0,
        le=POSTGRES_BIGINT_MAX,
        description="Server-controlled projection revision.",
    )
    updated_at: UtcDatetime
