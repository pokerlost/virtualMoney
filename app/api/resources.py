"""Typed lifespan-owned runtime resources."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

type SessionFactory = async_sessionmaker[AsyncSession]


class ApplicationResources:
    """Own the engine and session factory for one application lifespan."""

    __slots__ = ("engine", "session_factory")

    def __init__(
        self,
        *,
        engine: AsyncEngine | None,
        session_factory: SessionFactory | None,
    ) -> None:
        """Store process-scoped infrastructure resources."""
        self.engine = engine
        self.session_factory = session_factory
