"""Get account balance HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.accounts.dependencies import provide_get_account_balance
from api.schemas.requests import GetBalanceRequest
from api.schemas.responses import AccountBalanceResponse, ApplicationResponse
from api.types import HandlerResult
from application.accounts import GetAccountBalanceHandler

router = APIRouter()


@router.post(
    path=".getBalance",
    response_model=ApplicationResponse[AccountBalanceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get an account balance",
    description=(
        "Return posted and held projections plus availableBalanceMinor, derived as posted "
        "minus held. All values use integer minimal units."
    ),
    operation_id="virtualMoney.accounts.getBalance",
    openapi_extra={
        "x-pokerlost-authz": {
            "roles": [
                "user",
                "master",
                "auto",
            ],
        },
    },
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def get_account_balance(
    request: GetBalanceRequest,
    handler: Annotated[GetAccountBalanceHandler, Depends(provide_get_account_balance)],
) -> HandlerResult:
    """Delegate projection lookup to the application layer."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }
