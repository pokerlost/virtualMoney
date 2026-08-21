"""Accounts base router."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .create import router as create_router
from .get import router as get_router
from .get_balance import router as get_balance_router
from .get_financial_history import router as get_financial_history_router

router = APIRouter(prefix="/accounts", tags=[OpenAPITag.ACCOUNTS])
router.include_router(create_router)
router.include_router(get_router)
router.include_router(get_balance_router)
router.include_router(get_financial_history_router)
