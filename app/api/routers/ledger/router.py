"""Ledger base router."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .get import router as get_router
from .post import router as post_router
from .reverse import router as reverse_router

router = APIRouter(prefix="/ledger", tags=[OpenAPITag.LEDGER])
router.include_router(post_router)
router.include_router(get_router)
router.include_router(reverse_router)
