"""Единая стратегия имён и aliases для публичных API-моделей."""

from typing import Final

from pydantic import AliasChoices, AliasGenerator
from pydantic.alias_generators import to_camel, to_pascal


def _validation_alias(field_name: str) -> AliasChoices:
    """Возвращает публичные варианты входного имени Pydantic-поля."""
    return AliasChoices(to_camel(field_name), to_pascal(field_name))


API_ALIAS_GENERATOR: Final[AliasGenerator] = AliasGenerator(
    alias=to_camel,
    validation_alias=_validation_alias,
    serialization_alias=to_camel,
)
