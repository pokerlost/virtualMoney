"""Normalized optional ledger description type."""

from __future__ import annotations

from typing import Annotated

from pydantic import AfterValidator, Field


def _normalize_description(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("ledger description must not be blank")
    return normalized


type LedgerDescription = Annotated[
    str,
    Field(max_length=500),
    AfterValidator(_normalize_description),
]
