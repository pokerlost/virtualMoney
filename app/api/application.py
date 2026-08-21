"""FastAPI application factory and composition root."""

from __future__ import annotations

from importlib.metadata import version

from fastapi import FastAPI

from api.errors import configure_exception_handlers
from api.lifespan import create_application_lifespan
from api.openapi import API_DESCRIPTION, build_openapi_tags
from api.routes import configure_routers
from configuration import Settings
from observability import configure_observability, instrument_fastapi


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create one independently configured virtualMoney application."""
    application_settings = settings or Settings()
    configure_observability(application_settings)
    openapi_enabled = application_settings.application.openapi_enabled
    app = FastAPI(
        title=application_settings.application.service_name,
        description=API_DESCRIPTION,
        version=version("virtualMoney"),
        openapi_url="/openapi.json" if openapi_enabled else None,
        docs_url="/docs" if openapi_enabled else None,
        redoc_url="/redoc" if openapi_enabled else None,
        openapi_tags=build_openapi_tags(),
        lifespan=create_application_lifespan(application_settings),
    )
    configure_exception_handlers(app)
    configure_routers(app)
    instrument_fastapi(app, application_settings)
    return app
