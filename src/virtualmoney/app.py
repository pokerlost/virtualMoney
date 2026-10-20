"""FastAPI factory and process-owned resource lifecycle."""

from __future__ import annotations

import logging
import re
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import (
    AbstractAsyncContextManager,
    asynccontextmanager,
)
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, Response

from virtualmoney import observability
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


def create_app(
    settings: ServiceSettings | None = None,
    *,
    telemetry: observability.ObservabilitySettings | None = None,
) -> FastAPI:
    """Compose HTTP behavior without import-time settings or network effects."""
    resolved_settings = settings if settings is not None else ServiceSettings()
    resolved_telemetry = (
        telemetry if telemetry is not None else observability.ObservabilitySettings()
    )
    LOGGER.setLevel(resolved_settings.log_level)
    http_logger = observability.request_logger(resolved_settings.log_level)
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
        incoming_ids = request.headers.getlist("X-Request-ID")
        incoming = incoming_ids[0] if len(incoming_ids) == 1 else ""
        request_id = incoming if REQUEST_ID.fullmatch(incoming) else str(uuid4())
        request.state.request_id = request_id
        started = perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            route = request.scope.get("route")
            http_logger.info(
                "http_request",
                extra={
                    "environment": resolved_telemetry.environment,
                    "request_id": request_id,
                    "operation": getattr(route, "path", "none"),
                    "status": status,
                    "duration_seconds": perf_counter() - started,
                },
            )

    application.include_router(health_router)
    application.description = (
        "Direct service origins do not require a routing header. Gateway HTTP calls "
        "use x-pokerlost-serviceId with an exact SDK ServiceId and an operation path "
        "without a service prefix. The routing header grants no authorization; "
        "protected operations still require their exact Bearer audience/scopes."
    )
    application.include_router(root.router)
    application.include_router(openapi.router)
    application.state.token_verifier = None
    configure_authorization_errors(application)
    if resolved_telemetry.metrics_enabled:
        observability.instrument(application)
    return application
