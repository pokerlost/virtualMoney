"""FastAPI application factory and composition root."""

from __future__ import annotations

from importlib.metadata import version
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from api.errors import configure_exception_handlers
from api.lifespan import create_application_lifespan
from api.openapi import (
    API_DESCRIPTION,
    add_pokerlost_service_extension,
    build_openapi_tags,
)
from api.routes import configure_routers
from configuration import Settings
from observability import configure_observability, instrument_fastapi


def configure_openapi(application: FastAPI, service_id: str) -> None:
    """Attach canonical top-level virtualMoney metadata to generated OpenAPI schema."""

    def openapi_with_service() -> dict[str, Any]:
        if application.openapi_schema is None:
            openapi_schema = get_openapi(
                title=application.title,
                summary=application.summary,
                description=application.description,
                version=application.version,
                openapi_version=application.openapi_version,
                servers=application.servers,
                terms_of_service=application.terms_of_service,
                contact=application.contact,
                license_info=application.license_info,
                routes=application.routes,
                tags=application.openapi_tags,
            )
            add_pokerlost_service_extension(openapi_schema, service_id)
            application.openapi_schema = openapi_schema
        return application.openapi_schema

    application.openapi = openapi_with_service  # type: ignore[method-assign]


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
    configure_openapi(app, application_settings.application.service_name)
    instrument_fastapi(app, application_settings)
    return app
