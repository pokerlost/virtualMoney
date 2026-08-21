"""Connect Alembic to service configuration and SQLAlchemy metadata."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from configuration import Settings
from persistence.database import models

__all__ = ("run_migrations_offline", "run_migrations_online")

# Importing the models facade registers every ORM table for autogeneration.

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = models.AccountModel.metadata


def _database_url() -> str:
    database_url = Settings().database.url
    if database_url is None:
        raise RuntimeError(
            "VIRTUALMONEY_DATABASE__URL is required to run Alembic migrations",
        )
    return str(database_url)


def run_migrations_offline() -> None:
    """Run migrations without creating an engine or connection."""
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def _run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        raise RuntimeError("Alembic configuration section is missing")
    configuration["sqlalchemy.url"] = _database_url()
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations through one temporary asynchronous engine."""
    asyncio.run(_run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
