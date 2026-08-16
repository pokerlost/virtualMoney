"""Factories асинхронных SQLAlchemy engine и sessionmaker."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_database_engine(database_url: str, *, echo: bool = False) -> AsyncEngine:
    """Создаёт lazy AsyncEngine без открытия соединения на import или при вызове factory.

    Args:
        database_url: URL PostgreSQL с driver `postgresql+asyncpg`.
        echo: Включает SQLAlchemy SQL echo; не предназначен для production credentials.

    Returns:
        AsyncEngine, который подключится к БД только при первой операции.
    """
    return create_async_engine(database_url, echo=echo, pool_pre_ping=True)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Создаёт factory независимых AsyncSession для request или Unit of Work boundary.

    Args:
        engine: Application-level AsyncEngine, которым владеет composition root.

    Returns:
        Typed sessionmaker; каждый вызов создаёт отдельную AsyncSession без global state.
    """
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
