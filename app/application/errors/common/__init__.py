"""Public common application errors."""

from __future__ import annotations

from .idempotency_conflict import IdempotencyConflict

__all__ = ("IdempotencyConflict",)
