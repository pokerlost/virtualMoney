"""Post ledger transaction HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.ledger.dependencies import provide_post_ledger_transaction
from api.schemas.orm import LedgerTransactionSchema
from api.schemas.requests import PostTransactionRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.ledger import PostTransactionHandler

router = APIRouter()


@router.post(
    path=".postTransaction",
    response_model=ApplicationResponse[LedgerTransactionSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Post an internal ledger transaction",
    description=(
        "Atomically post a balanced ADJUSTMENT and update materialized posted balances in "
        "the same PostgreSQL transaction."
    ),
    operation_id="ledger_post_transaction",
    responses={
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def post_ledger_transaction(
    request: PostTransactionRequest,
    handler: Annotated[
        PostTransactionHandler,
        Depends(provide_post_ledger_transaction),
    ],
) -> HandlerResult:
    """Delegate a balanced posting command to the application layer."""
    result = await handler.execute(request.to_command())
    return {
        "ok": True,
        "result": result,
    }
