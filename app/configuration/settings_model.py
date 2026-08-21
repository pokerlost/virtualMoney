"""Shared configuration for nested logical settings groups."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SettingsModel(BaseModel):
    """Apply immutable strict validation to nested settings groups."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=True,
    )
