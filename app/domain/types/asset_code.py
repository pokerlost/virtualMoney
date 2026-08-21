"""Canonical internal asset code."""

from __future__ import annotations

import re
from typing import Annotated, Final

from pydantic import AfterValidator

ASSET_CODE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[A-Z][A-Z0-9_]{1,15}$")


def _normalize_asset_code(value: str) -> str:
    normalized = value.strip().upper()
    if ASSET_CODE_PATTERN.fullmatch(normalized) is None:
        raise ValueError("asset code has an invalid format")
    return normalized


type AssetCode = Annotated[str, AfterValidator(_normalize_asset_code)]
