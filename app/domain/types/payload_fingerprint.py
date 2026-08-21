"""Canonical SHA-256 semantic payload fingerprint."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

type PayloadFingerprint = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
