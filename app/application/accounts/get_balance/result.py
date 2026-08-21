"""Account balance application read model."""

from __future__ import annotations

from pydantic import Field

from domain import ValueModel
from domain.money import POSTGRES_BIGINT_MAX
from domain.types import (
    NonNegativeMoneyMinor,
    NonNilUUID,
    SignedMoneyMinor,
    UtcDatetime,
)


class AccountBalanceDetails(ValueModel):
    """Posted and held projection with authoritative asset metadata."""

    account_id: NonNilUUID
    asset_id: NonNilUUID
    posted_balance_minor: SignedMoneyMinor
    held_balance_minor: NonNegativeMoneyMinor
    available_balance_minor: SignedMoneyMinor
    version: int = Field(strict=True, ge=0, le=POSTGRES_BIGINT_MAX)
    updated_at: UtcDatetime
