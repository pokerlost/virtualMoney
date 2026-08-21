"""Normalized bounded full-compensation reason."""

from __future__ import annotations

from typing import Annotated

from pydantic import AfterValidator, Field


def _normalize_refund_reason(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("refund reason must not be blank")
    return normalized


type RefundReason = Annotated[
    str,
    Field(min_length=1, max_length=500),
    AfterValidator(_normalize_refund_reason),
]
