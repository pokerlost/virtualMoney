"""Funds hold lifecycle states."""

from __future__ import annotations

from enum import StrEnum


class HoldStatus(StrEnum):
    """Represent a full hold lifecycle without partial transitions."""

    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
    CAPTURED = "CAPTURED"
