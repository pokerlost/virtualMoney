"""Supported deployment environments."""

from __future__ import annotations

from enum import StrEnum


class Environment(StrEnum):
    """Name the service runtime environment."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
