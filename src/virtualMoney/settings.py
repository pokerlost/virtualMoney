"""Validated process settings loaded only when an application is constructed."""

from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceSettings(BaseSettings):
    """Values for enabled process resources, with safe error rendering."""

    model_config = SettingsConfigDict(
        env_prefix="VIRTUALMONEY_",
        extra="ignore",
        validate_default=True,
        validate_by_name=True,
        hide_input_in_errors=True,
    )

    logLevel: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
