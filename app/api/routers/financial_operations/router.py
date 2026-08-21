"""Financial operations base router."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .get import router as get_router
from .refund import router as refund_router

router = APIRouter(
    prefix="/financialOperations",
    tags=[OpenAPITag.FINANCIAL_OPERATIONS],
)
router.include_router(get_router)
router.include_router(refund_router)
