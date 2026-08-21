"""Holds base router."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .capture import router as capture_router
from .get import router as get_router
from .release import router as release_router
from .reserve import router as reserve_router

router = APIRouter(prefix="/holds", tags=[OpenAPITag.HOLDS])
router.include_router(reserve_router)
router.include_router(get_router)
router.include_router(release_router)
router.include_router(capture_router)
