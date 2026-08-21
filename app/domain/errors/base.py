"""Base domain validation error."""

from __future__ import annotations


class DomainValidationError(ValueError):
    """Base client-safe failure for pure financial invariants."""

    error_code = "INVALID_DOMAIN_VALUE"
    public_message = "The submitted data violates the financial model rules."
