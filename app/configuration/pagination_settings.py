"""Cursor pagination settings."""

from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from .settings_model import SettingsModel


class PaginationSettings(SettingsModel):
    """Configure default and maximum immutable history page sizes."""

    default_limit: int = Field(default=50, ge=1, le=500)
    maximum_limit: int = Field(default=100, ge=1, le=500)

    @model_validator(mode="after")
    def validate_limits(self) -> Self:
        """Keep the default within the deployment maximum."""
        if self.default_limit > self.maximum_limit:
            raise ValueError("pagination default_limit must not exceed maximum_limit")
        return self
