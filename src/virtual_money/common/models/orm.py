"""Pydantic-основа для schemas, создаваемых из object attributes."""

from pydantic import ConfigDict

from virtual_money.common.models.base import AppBaseModel


class OrmSchemaBase(AppBaseModel):
    """Разрешает безопасное построение Pydantic schema из ORM/domain-like objects."""

    model_config = ConfigDict(from_attributes=True)
