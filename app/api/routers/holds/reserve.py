"""Reserve hold HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.holds.dependencies import provide_reserve_hold
from api.schemas.orm import HoldSchema
from api.schemas.requests import ReserveHoldRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.holds import ReserveHoldHandler

router = APIRouter()


@router.post(
    path=".reserveHold",
    response_model=ApplicationResponse[HoldSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Reserve account funds",
    description=(
        "Create one ACTIVE full-only hold and increase heldBalanceMinor without posting a "
        "ledger transaction."
    ),
    operation_id="virtualMoney.holds.reserveHold",
    openapi_extra={
        "x-pokerlost-authz": {
            "roles": [
                "auto",
            ],
        }
    },
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def reserve_hold(
    request: ReserveHoldRequest,
    handler: Annotated[ReserveHoldHandler, Depends(provide_reserve_hold)],
) -> HandlerResult:
    """Delegate hold reservation to the application layer."""
    result = await handler.execute(request.to_command())
    return {
        "ok": True,
        "result": result,
    }
