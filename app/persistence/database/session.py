"""Factories for the asynchronous SQLAlchemy engine and sessionmaker."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from configuration import DatabaseSettings


def create_database_engine(settings: DatabaseSettings) -> AsyncEngine:
    """Create a lazy engine from validated PostgreSQL settings."""
    if settings.url is None:
        raise RuntimeError("database URL is not configured")
    return create_async_engine(
        str(settings.url),
        echo=settings.echo,
        hide_parameters=True,
        pool_pre_ping=True,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        pool_timeout=settings.pool_timeout_seconds,
        connect_args={"command_timeout": settings.command_timeout_seconds},
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create independent sessions that retain loaded scalar state after commit."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
