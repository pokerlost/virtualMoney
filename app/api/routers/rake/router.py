"""Rake base router."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .charge import router as charge_router

router = APIRouter(prefix="/rake", tags=[OpenAPITag.RAKE])
router.include_router(charge_router)
