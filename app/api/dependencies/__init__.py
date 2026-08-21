"""Shared FastAPI boundary dependencies."""

from __future__ import annotations

from .database import DatabaseSession
from .resources import ApplicationResourcesDep
from .settings import ApplicationSettingsDep

__all__ = (
    "ApplicationResourcesDep",
    "ApplicationSettingsDep",
    "DatabaseSession",
)
