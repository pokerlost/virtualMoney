"""Capture hold HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.holds.dependencies import provide_capture_hold
from api.schemas.orm import HoldSchema
from api.schemas.requests import CaptureHoldRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.holds import CaptureHoldHandler

router = APIRouter()


@router.post(
    path=".captureHold",
    response_model=ApplicationResponse[HoldSchema],
    status_code=status.HTTP_200_OK,
    summary="Capture a hold in full",
    description=(
        "Transfer the authoritative held amount through one immutable HOLD_CAPTURE journal. "
        "Partial capture and caller-provided amounts are unsupported."
    ),
    operation_id="holds_capture_hold",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def capture_hold(
    request: CaptureHoldRequest,
    handler: Annotated[CaptureHoldHandler, Depends(provide_capture_hold)],
) -> HandlerResult:
    """Delegate full capture to the application layer."""
    result = await handler.execute(request.to_command())
    return {
        "ok": True,
        "result": result,
    }
