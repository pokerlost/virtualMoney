"""Durable player table-position states."""

from __future__ import annotations

from enum import StrEnum


class PlayerTablePositionStatus(StrEnum):
    """Represent a player's durable financial lifecycle at a table."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
