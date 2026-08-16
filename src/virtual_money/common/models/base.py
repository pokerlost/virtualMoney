"""Общая конфигурация Pydantic v2 для моделей сервиса."""

from pydantic import BaseModel, ConfigDict

from virtual_money.common.naming import API_ALIAS_GENERATOR


class AppBaseModel(BaseModel):
    """Задаёт строгую validation и единую alias policy для Pydantic-моделей."""

    model_config = ConfigDict(
        alias_generator=API_ALIAS_GENERATOR,
        extra="forbid",
        serialize_by_alias=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        validate_by_alias=True,
        validate_by_name=True,
    )
