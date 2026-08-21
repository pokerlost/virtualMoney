"""HTTP server settings."""

from __future__ import annotations

from pydantic import Field

from .settings_model import SettingsModel


class HTTPSettings(SettingsModel):
    """Configure Uvicorn binding."""

    host: str = Field(default="127.0.0.1", min_length=1, max_length=255)
    port: int = Field(default=8000, ge=1, le=65535)
