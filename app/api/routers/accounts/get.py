"""Get account HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.accounts.dependencies import provide_get_account
from api.schemas.orm import AccountSchema
from api.schemas.requests import GetAccountRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.accounts import GetAccountHandler

router = APIRouter()


@router.post(
    path=".getAccount",
    response_model=ApplicationResponse[AccountSchema],
    status_code=status.HTTP_200_OK,
    summary="Get a financial account",
    description="Return account metadata without embedding its balance projection.",
    operation_id="accounts_get_account",
    openapi_extra={
        "x-pokerlost-authz": {
            "actors": ["service"],
            "permissions": ["accounts_get_account"],
    },
    },
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def get_account(
    request: GetAccountRequest,
    handler: Annotated[GetAccountHandler, Depends(provide_get_account)],
) -> HandlerResult:
    """Delegate account lookup to the application layer."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }
