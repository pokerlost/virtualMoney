"""Canonical business reference namespace and pair validation."""

from __future__ import annotations

import re
from typing import Annotated, Final

from pydantic import AfterValidator

from .non_nil_uuid import NonNilUUID

REFERENCE_TYPE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


def _normalize_reference_type(value: str) -> str:
    normalized = value.strip().upper()
    if REFERENCE_TYPE_PATTERN.fullmatch(normalized) is None:
        raise ValueError("reference type has an invalid format")
    return normalized


type ReferenceType = Annotated[str, AfterValidator(_normalize_reference_type)]


def validate_reference_pair(
    reference_type: ReferenceType | None,
    reference_id: NonNilUUID | None,
) -> None:
    """Require a reference namespace and identifier together."""
    if (reference_type is None) != (reference_id is None):
        raise ValueError("reference_type and reference_id must be supplied together")
