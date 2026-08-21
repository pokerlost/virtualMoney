"""Get asset by code HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.assets.dependencies import provide_get_asset_by_code
from api.schemas.orm import AssetSchema
from api.schemas.requests import GetAssetByCodeRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.assets import GetAssetByCodeHandler

router = APIRouter()


@router.post(
    path=".getAssetByCode",
    response_model=ApplicationResponse[AssetSchema],
    status_code=status.HTTP_200_OK,
    summary="Get an asset by code",
    description="Return internal asset metadata by its normalized canonical code.",
    operation_id="assets_get_asset_by_code",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def get_asset_by_code(
    request: GetAssetByCodeRequest,
    handler: Annotated[GetAssetByCodeHandler, Depends(provide_get_asset_by_code)],
) -> HandlerResult:
    """Delegate canonical-code lookup to the application layer."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }
