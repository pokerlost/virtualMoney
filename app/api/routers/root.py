"""Parameterless service endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.openapi import OpenAPITag
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult

router = APIRouter(tags=[OpenAPITag.SERVICE])


@router.get(
    path="/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get service root",
    description="Return the minimal virtualMoney service availability response.",
    operation_id="virtualMoney.root",
    openapi_extra={
        "x-pokerlost-authz": {
            "public": True,
        },
    },
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
def get_service_root() -> HandlerResult:
    """Return the minimal root success contract."""
    return {
        "ok": True,
        "result": None,
    }
