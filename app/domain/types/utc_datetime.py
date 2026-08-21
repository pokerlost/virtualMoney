"""Timezone-aware datetime normalized to UTC."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, AwareDatetime


def _normalize_utc(value: datetime) -> datetime:
    return value.astimezone(UTC)


type UtcDatetime = Annotated[AwareDatetime, AfterValidator(_normalize_utc)]
