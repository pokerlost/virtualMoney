"""Signed ledger posting value."""

from __future__ import annotations

from domain.types import NonNilUUID, NonZeroMoneyMinor
from domain.value_model import ValueModel


class Posting(ValueModel):
    """Signed change to one financial account in minimal units."""

    account_id: NonNilUUID
    amount_minor: NonZeroMoneyMinor
