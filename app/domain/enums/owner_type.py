"""Opaque account owner namespaces."""

from __future__ import annotations

from enum import StrEnum


class OwnerType(StrEnum):
    """Namespace owner identifiers for users, tables, and the system."""

    USER = "USER"
    TABLE = "TABLE"
    SYSTEM = "SYSTEM"
