"""Typed access to composition-root settings."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from configuration import Settings


def get_settings(request: Request) -> Settings:
    """Return validated settings from application state."""
    settings = request.app.state.settings
    if not isinstance(settings, Settings):
        raise RuntimeError("application settings are not initialized")
    return settings


type ApplicationSettingsDep = Annotated[Settings, Depends(get_settings)]
