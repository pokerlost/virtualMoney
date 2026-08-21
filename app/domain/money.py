"""PostgreSQL BIGINT monetary bounds."""

from __future__ import annotations

from typing import Final

POSTGRES_BIGINT_MIN: Final[int] = -(2**63)
POSTGRES_BIGINT_MAX: Final[int] = 2**63 - 1


def fits_postgres_bigint(value: object) -> bool:
    """Return whether a strict integer fits PostgreSQL signed BIGINT."""
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and POSTGRES_BIGINT_MIN <= value <= POSTGRES_BIGINT_MAX
    )
