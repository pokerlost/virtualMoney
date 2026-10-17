"""FastAPI factory and process-owned resource lifecycle."""

from __future__ import annotations

import logging
import re
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response

from virtualMoney.authorization import configureAuthorizationErrors
from virtualMoney.errors import configureErrorHandlers
from virtualMoney.resources import ApplicationResources, getResources
from virtualMoney.routers import openapi, root
from virtualMoney.settings import ServiceSettings

REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
LOGGER = logging.getLogger("virtualMoney")


def createLifespan(
    settings: ServiceSettings,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None, bool | None]]:
    """Acquire enabled resources and dispose them even after partial startup."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.resources = ApplicationResources()
        try:
            yield
        finally:
            del application.state.resources

    return lifespan


def createApp(settings: ServiceSettings | None = None) -> FastAPI:
    """Compose HTTP behavior without import-time settings or network effects."""
    resolvedSettings = settings if settings is not None else ServiceSettings()
    LOGGER.setLevel(resolvedSettings.logLevel)
    application = FastAPI(
        title="virtualMoney",
        lifespan=createLifespan(resolvedSettings),
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    configureErrorHandlers(application)

    @application.middleware("http")
    async def correlationId(
        request: Request, callNext: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        incoming = request.headers.get("X-Request-ID", "")
        requestId = incoming if REQUEST_ID.fullmatch(incoming) else str(uuid4())
        request.state.requestId = requestId
        response = await callNext(request)
        response.headers["X-Request-ID"] = requestId
        return response

    @application.get("/health/live", include_in_schema=False)
    async def live() -> dict[str, str]:
        return {"status": "alive"}

    @application.get("/health/ready", include_in_schema=False)
    async def ready(request: Request) -> dict[str, str]:
        resources = getResources(request)
        if not resources.ready:
            raise HTTPException(status_code=503, detail="Required dependency unavailable")
        return {"status": "ready"}

    application.include_router(root.router)
    application.include_router(openapi.router)
    application.state.tokenVerifier = None
    configureAuthorizationErrors(application)
    return application
