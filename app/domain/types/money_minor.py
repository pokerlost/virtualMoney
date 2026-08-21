"""Validated PostgreSQL BIGINT monetary types."""

from __future__ import annotations

from typing import Annotated

from pydantic import AfterValidator, Field

from domain.money import POSTGRES_BIGINT_MAX, POSTGRES_BIGINT_MIN


def _reject_zero(value: int) -> int:
    if value == 0:
        raise ValueError("money amount must not be zero")
    return value


type SignedMoneyMinor = Annotated[
    int,
    Field(strict=True, ge=POSTGRES_BIGINT_MIN, le=POSTGRES_BIGINT_MAX),
]
type ReversibleMoneyMinor = Annotated[
    int,
    Field(strict=True, ge=-POSTGRES_BIGINT_MAX, le=POSTGRES_BIGINT_MAX),
]
type PositiveMoneyMinor = Annotated[
    int,
    Field(strict=True, gt=0, le=POSTGRES_BIGINT_MAX),
]
type NonNegativeMoneyMinor = Annotated[
    int,
    Field(strict=True, ge=0, le=POSTGRES_BIGINT_MAX),
]
type NonZeroMoneyMinor = Annotated[
    int,
    Field(strict=True, ge=-POSTGRES_BIGINT_MAX, le=POSTGRES_BIGINT_MAX),
    AfterValidator(_reject_zero),
]
