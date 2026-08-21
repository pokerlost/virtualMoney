"""Pydantic Logfire settings."""

from __future__ import annotations

from typing import Literal

from .settings_model import SettingsModel

type LogfireLevel = Literal[
    "trace",
    "debug",
    "info",
    "notice",
    "warn",
    "warning",
    "error",
    "fatal",
]


class LogfireSettings(SettingsModel):
    """Control telemetry instrumentation and export policy."""

    enabled: bool = True
    send_to_logfire: bool = False
    console: bool = True
    minimum_level: LogfireLevel = "info"
