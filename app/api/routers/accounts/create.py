"""Create account HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.accounts.dependencies import provide_create_account
from api.schemas.orm import AccountSchema
from api.schemas.requests import CreateAccountRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.accounts import CreateAccountHandler

router = APIRouter()


@router.post(
    path=".createAccount",
    response_model=ApplicationResponse[AccountSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Create a financial account",
    description=(
        "Create account metadata and its zero balance projection in one transaction. "
        "A stable accountId makes exact retries idempotent."
    ),
    operation_id="virtualMoney.accounts.createAccount",
    openapi_extra={
        "x-pokerlost-authz": {
            "roles": [
                "master",
                "auto",
            ],
        },
    },
    responses={
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def create_account(
    request: CreateAccountRequest,
    handler: Annotated[CreateAccountHandler, Depends(provide_create_account)],
) -> HandlerResult:
    """Delegate account creation to the application layer."""
    result = await handler.execute(request.to_command())
    return {
        "ok": True,
        "result": result,
    }
