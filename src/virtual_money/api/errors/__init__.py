"""Централизованное преобразование исключений в безопасные HTTP responses."""

from virtual_money.api.errors.handlers import configure_exception_handlers

__all__ = ["configure_exception_handlers"]
