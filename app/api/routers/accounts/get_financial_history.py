"""Get account financial history HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.accounts.dependencies import provide_get_account_history
from api.schemas.requests import GetFinancialHistoryRequest
from api.schemas.responses import (
    AccountHistoryItemResponse,
    ApplicationResponse,
    PaginationResponse,
)
from api.types import HandlerResult
from application.accounts import GetFinancialHistoryHandler

router = APIRouter()


@router.post(
    path=".getFinancialHistory",
    response_model=ApplicationResponse[PaginationResponse[AccountHistoryItemResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get account financial history",
    description=(
        "Return a descending keyset page of account-relative ledger transactions, signed "
        "amounts, business references, and explicit reversal links."
    ),
    operation_id="accounts_get_financial_history",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def get_account_financial_history(
    request: GetFinancialHistoryRequest,
    handler: Annotated[GetFinancialHistoryHandler, Depends(provide_get_account_history)],
) -> HandlerResult:
    """Delegate bounded history lookup to the application layer."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }
