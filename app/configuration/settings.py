"""Composition of all environment-backed settings groups."""

from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .application_settings import ApplicationSettings
from .database_settings import DatabaseSettings
from .environment import Environment
from .http_settings import HTTPSettings
from .logfire_settings import LogfireSettings
from .pagination_settings import PaginationSettings


class Settings(BaseSettings):
    """Load all runtime configuration once at the composition boundary."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="VIRTUALMONEY_",
        extra="ignore",
        case_sensitive=False,
        str_strip_whitespace=True,
        validate_default=True,
    )

    application: ApplicationSettings = Field(default_factory=ApplicationSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    http: HTTPSettings = Field(default_factory=HTTPSettings)
    pagination: PaginationSettings = Field(default_factory=PaginationSettings)
    logfire: LogfireSettings = Field(default_factory=LogfireSettings)

    @model_validator(mode="after")
    def validate_production_requirements(self) -> Self:
        """Require PostgreSQL configuration in production."""
        if self.application.environment is Environment.PRODUCTION and self.database.url is None:
            raise ValueError("database URL is required in production")
        return self
