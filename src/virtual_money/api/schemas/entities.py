"""Общие поля API schemas для сущностей сервиса."""

from uuid import UUID

from pydantic import Field

from virtual_money.common.models.orm import OrmSchemaBase


class EntitySchemaBase(OrmSchemaBase):
    """Определяет минимальный публичный идентификатор entity response."""

    id: UUID = Field(description="Уникальный идентификатор сущности.")
