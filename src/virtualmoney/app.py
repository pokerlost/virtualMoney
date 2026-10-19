"""FastAPI factory and process-owned resource lifecycle."""

from __future__ import annotations

import logging
import re
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import (
    AbstractAsyncContextManager,
    asynccontextmanager,
)
from uuid import uuid4

from fastapi import FastAPI, Request, Response

from virtualmoney.api.health import router as health_router
from virtualmoney.authorization import configure_authorization_errors
from virtualmoney.errors import configure_error_handlers
from virtualmoney.resources import ApplicationResources
from virtualmoney.routers import openapi, root
from virtualmoney.settings import ServiceSettings

REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
LOGGER = logging.getLogger("virtualMoney")


def create_lifespan(
    settings: ServiceSettings,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None, bool | None]]:
    """Acquire enabled resources and dispose them after partial startup."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.resources = ApplicationResources()
        try:
            yield
        finally:
            del application.state.resources

    return lifespan


def create_app(settings: ServiceSettings | None = None) -> FastAPI:
    """Compose HTTP behavior without import-time settings or network effects."""
    resolved_settings = settings if settings is not None else ServiceSettings()
    LOGGER.setLevel(resolved_settings.log_level)
    application = FastAPI(
        title="virtualMoney",
        lifespan=create_lifespan(resolved_settings),
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    configure_error_handlers(application)

    @application.middleware("http")
    async def correlation_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        incoming = request.headers.get("X-Request-ID", "")
        request_id = incoming if REQUEST_ID.fullmatch(incoming) else str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    application.include_router(health_router)
    application.include_router(root.router)
    application.include_router(openapi.router)
    application.state.token_verifier = None
    configure_authorization_errors(application)
    return application
