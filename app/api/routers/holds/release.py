"""Release hold HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.holds.dependencies import provide_release_hold
from api.schemas.orm import HoldSchema
from api.schemas.requests import ReleaseHoldRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.holds import ReleaseHoldHandler

router = APIRouter()


@router.post(
    path=".releaseHold",
    response_model=ApplicationResponse[HoldSchema],
    status_code=status.HTTP_200_OK,
    summary="Release a hold in full",
    description=(
        "Transition one ACTIVE hold to RELEASED and decrease heldBalanceMinor without a "
        "ledger posting. Partial release is unsupported."
    ),
    operation_id="virtualMoney.holds.releaseHold",
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
async def release_hold(
    request: ReleaseHoldRequest,
    handler: Annotated[ReleaseHoldHandler, Depends(provide_release_hold)],
) -> HandlerResult:
    """Delegate full release to the application layer."""
    result = await handler.execute(request.to_command())
    return {
        "ok": True,
        "result": result,
    }
