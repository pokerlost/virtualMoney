"""Централизованная загрузка и validation настроек приложения."""

from enum import StrEnum

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Поддерживаемые runtime-окружения сервиса."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    """Допустимые уровни логирования приложения."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Хранит validated configuration без произвольного чтения environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="VIRTUAL_MONEY_",
        extra="ignore",
        case_sensitive=False,
        str_strip_whitespace=True,
        validate_default=True,
    )

    application_name: str = Field(default="virtualMoney", min_length=1)
    environment: Environment = Environment.LOCAL
    log_level: LogLevel = LogLevel.INFO
    database_url: PostgresDsn | None = None

    @field_validator("database_url")
    @classmethod
    def validate_database_driver(cls, value: PostgresDsn | None) -> PostgresDsn | None:
        """Запрещает синхронный PostgreSQL driver в асинхронном приложении."""
        if value is not None and value.scheme != "postgresql+asyncpg":
            raise ValueError("database_url must use the postgresql+asyncpg scheme")
        return value
