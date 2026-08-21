"""Get ledger transaction HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.ledger.dependencies import provide_get_ledger_transaction
from api.schemas.orm import LedgerTransactionSchema
from api.schemas.requests import GetTransactionRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.ledger import GetTransactionHandler

router = APIRouter()


@router.post(
    path=".getTransaction",
    response_model=ApplicationResponse[LedgerTransactionSchema],
    status_code=status.HTTP_200_OK,
    summary="Get a ledger transaction",
    description="Return an immutable posted journal and its explicitly loaded entries.",
    operation_id="ledger_get_transaction",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def get_ledger_transaction(
    request: GetTransactionRequest,
    handler: Annotated[
        GetTransactionHandler,
        Depends(provide_get_ledger_transaction),
    ],
) -> HandlerResult:
    """Delegate immutable journal lookup to the application layer."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }
