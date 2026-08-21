"""Internal pagination limit type."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

type PaginationLimit = Annotated[int, Field(strict=True, ge=1, le=500)]
