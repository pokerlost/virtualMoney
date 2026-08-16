"""Базовые Pydantic-модели сервиса."""

from virtual_money.common.models.base import AppBaseModel
from virtual_money.common.models.orm import OrmSchemaBase

__all__ = ["AppBaseModel", "OrmSchemaBase"]
