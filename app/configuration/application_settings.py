"""Logical application settings."""

from __future__ import annotations

from typing import Literal

from .environment import Environment
from .settings_model import SettingsModel


class ApplicationSettings(SettingsModel):
    """Configure logical identity and developer-facing behavior."""

    service_name: Literal["virtualMoney"] = "virtualMoney"
    environment: Environment = Environment.LOCAL
    openapi_enabled: bool = True
