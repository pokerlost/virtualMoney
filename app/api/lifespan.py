"""FastAPI lifespan for long-lived infrastructure resources."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from api.resources import ApplicationResources, SessionFactory
from configuration import Settings
from observability import instrument_database
from persistence.database import create_database_engine, create_session_factory

type ApplicationLifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def create_application_lifespan(settings: Settings) -> ApplicationLifespan:
    """Create and dispose runtime resources without migrations or availability checks."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine: AsyncEngine | None = None
        session_factory: SessionFactory | None = None
        if settings.database.url is not None:
            engine = create_database_engine(settings.database)
            instrument_database(engine, settings)
            session_factory = create_session_factory(engine)

        app.state.resources = ApplicationResources(
            engine=engine,
            session_factory=session_factory,
        )
        app.state.settings = settings
        try:
            yield
        finally:
            app.state.resources = None
            app.state.settings = None
            if engine is not None:
                await engine.dispose()

    return lifespan
