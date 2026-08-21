"""Shared immutable ledger validation helpers."""

from __future__ import annotations

from typing import Final

from domain.errors import InvalidPosting, LedgerTransactionUnbalanced

from .posting import Posting

MAX_LEDGER_ENTRIES: Final[int] = 100


def validate_postings(postings: tuple[Posting, ...]) -> None:
    """Validate cardinality and the zero-sum invariant."""
    if not 2 <= len(postings) <= MAX_LEDGER_ENTRIES:
        raise InvalidPosting("ledger transaction must contain between 2 and 100 postings")
    if sum(posting.amount_minor for posting in postings) != 0:
        raise LedgerTransactionUnbalanced()
