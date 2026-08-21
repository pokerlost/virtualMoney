"""Table positions base router."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .buy_in import router as buy_in_router
from .cash_out import router as cash_out_router
from .get import router as get_router
from .get_operations import router as get_operations_router
from .re_buy import router as re_buy_router

router = APIRouter(prefix="/tablePositions", tags=[OpenAPITag.TABLE_POSITIONS])
router.include_router(buy_in_router)
router.include_router(re_buy_router)
router.include_router(cash_out_router)
router.include_router(get_router)
router.include_router(get_operations_router)
