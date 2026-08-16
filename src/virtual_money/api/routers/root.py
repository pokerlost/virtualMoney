"""Корневой endpoint базовой доступности HTTP-приложения."""

from fastapi import APIRouter, status

from virtual_money.api.schemas.responses import ApiResponse, create_success_response

router = APIRouter(tags=["Service"])


@router.get(
    "/",
    response_model=ApiResponse[None],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Проверить доступность HTTP-приложения",
    description=(
        "Подтверждает, что FastAPI-приложение принимает HTTP-запросы. "
        "Endpoint не проверяет PostgreSQL или другие зависимости и не является readiness probe."
    ),
    operation_id="get_service_root",
    responses={
        status.HTTP_200_OK: {
            "description": "HTTP-приложение доступно.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApiResponse[None],
            "description": "Неожиданная внутренняя ошибка приложения.",
        },
    },
)
def get_service_root() -> ApiResponse[None]:
    """Возвращает успешный envelope без обращения к infrastructure dependencies."""
    return create_success_response(result=None, status_code=status.HTTP_200_OK)
