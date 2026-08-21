"""Shared keyset pagination interface."""

from __future__ import annotations

from .pagination_cursor import PaginationCursor
from .pagination_cursor_codec import PaginationCursorCodec
from .pagination_input import CURSOR_MAX_LENGTH, PaginationInput
from .pagination_limit import PaginationLimit
from .pagination_page import PaginationPage
from .pagination_policy import PaginationPolicy

__all__ = (
    "CURSOR_MAX_LENGTH",
    "PaginationCursor",
    "PaginationCursorCodec",
    "PaginationInput",
    "PaginationLimit",
    "PaginationPage",
    "PaginationPolicy",
)
