"""Immutable hold audit operation types."""

from __future__ import annotations

from enum import StrEnum


class HoldOperationType(StrEnum):
    """Classify completed hold operations."""

    RESERVE = "RESERVE"
    RELEASE = "RELEASE"
    CAPTURE = "CAPTURE"
