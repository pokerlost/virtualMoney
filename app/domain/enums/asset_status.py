"""Internal asset lifecycle states."""

from __future__ import annotations

from enum import StrEnum


class AssetStatus(StrEnum):
    """Control whether an asset accepts new financial operations."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
