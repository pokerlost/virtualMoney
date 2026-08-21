"""PostgreSQL runtime settings."""

from __future__ import annotations

from pydantic import Field, PostgresDsn, field_validator

from .settings_model import SettingsModel


class DatabaseSettings(SettingsModel):
    """Configure the async SQLAlchemy engine without opening it."""

    url: PostgresDsn | None = None
    command_timeout_seconds: float = Field(default=5.0, gt=0, le=60)
    pool_timeout_seconds: float = Field(default=5.0, gt=0, le=60)
    pool_size: int = Field(default=5, ge=1, le=100)
    max_overflow: int = Field(default=10, ge=0, le=100)
    echo: bool = False

    @field_validator("url")
    @classmethod
    def validate_async_driver(cls, value: PostgresDsn | None) -> PostgresDsn | None:
        """Reject synchronous and non-PostgreSQL URLs."""
        if value is not None and value.scheme != "postgresql+asyncpg":
            raise ValueError("database URL must use the postgresql+asyncpg scheme")
        return value
