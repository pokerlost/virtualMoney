"""Reverse ledger transaction HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.ledger.dependencies import provide_reverse_ledger_transaction
from api.schemas.orm import LedgerTransactionSchema
from api.schemas.requests import ReverseTransactionRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.ledger import ReverseTransactionHandler

router = APIRouter()


@router.post(
    path=".reverseTransaction",
    response_model=ApplicationResponse[LedgerTransactionSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Fully reverse a ledger transaction",
    description=(
        "Create one immutable REVERSAL with opposite entries. The original journal remains "
        "unchanged, and partial reversal is unsupported."
    ),
    operation_id="virtualMoney.ledger.reverseTransaction",
    openapi_extra={
        "x-pokerlost-authz": {
            "roles": [
                "master",
                "auto",
            ],
        },
    },
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def reverse_ledger_transaction(
    request: ReverseTransactionRequest,
    handler: Annotated[
        ReverseTransactionHandler,
        Depends(provide_reverse_ledger_transaction),
    ],
) -> HandlerResult:
    """Delegate full reversal to the application layer."""
    result = await handler.execute(request.to_command())
    return {
        "ok": True,
        "result": result,
    }
