"""Assets base router."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .get import router as get_router
from .get_by_code import router as get_by_code_router

router = APIRouter(prefix="/assets", tags=[OpenAPITag.ASSETS])
router.include_router(get_router)
router.include_router(get_by_code_router)
