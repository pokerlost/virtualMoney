"""Request-scoped transactional SQLAlchemy session dependency."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .resources import ApplicationResourcesDep


async def get_database_session(
    resources: ApplicationResourcesDep,
) -> AsyncIterator[AsyncSession]:
    """Yield one transaction that commits before the response is sent."""
    session_factory = resources.session_factory
    if session_factory is None:
        raise RuntimeError("database is not configured")
    async with session_factory.begin() as session:
        yield session


type DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_database_session, scope="function"),
]
