"""Application factory и сборка FastAPI transport layer."""

from fastapi import FastAPI

from virtual_money import __version__
from virtual_money.api.errors import configure_exception_handlers
from virtual_money.api.routers import root_router
from virtual_money.configuration import Settings

APPLICATION_DESCRIPTION = (
    "HTTP API сервиса внутренних игровых средств платформы онлайн-покера. "
    "Финансовые endpoints будут добавляться отдельными этапами."
)

OPENAPI_TAGS = [
    {
        "name": "Service",
        "description": "Базовые endpoints доступности HTTP-приложения.",
    }
]


def configure_routers(app: FastAPI) -> None:
    """Регистрирует routers текущего этапа в FastAPI application.

    Args:
        app: Изменяемый экземпляр FastAPI, создаваемый composition root.
    """
    app.include_router(root_router)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Создаёт и полностью конфигурирует FastAPI application.

    Args:
        settings: Явно переданные настройки или настройки, загруженные из environment.

    Returns:
        Новый независимый экземпляр FastAPI без открытых DB connections.
    """
    application_settings = settings or Settings()
    app = FastAPI(
        title=application_settings.application_name,
        description=APPLICATION_DESCRIPTION,
        version=__version__,
        openapi_tags=OPENAPI_TAGS,
    )
    configure_exception_handlers(app)
    configure_routers(app)
    return app
