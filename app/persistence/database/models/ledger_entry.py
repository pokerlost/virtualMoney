"""SQLAlchemy mapping for an immutable ledger entry."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.database import UUIDModel
from persistence.database.mixins import CreatedAtMixin

if TYPE_CHECKING:
    from .account import AccountModel
    from .ledger_transaction import LedgerTransactionModel


class LedgerEntryModel(CreatedAtMixin, UUIDModel):
    """Persistence representation of one immutable signed posting row."""

    __tablename__ = "ledger_entries"
    __table_args__ = (
        CheckConstraint(
            "amount_minor <> 0",
            name="ck_ledger_entries_amount_non_zero",
        ),
        CheckConstraint(
            "amount_minor <> -9223372036854775808",
            name="ck_ledger_entries_amount_reversible",
        ),
        CheckConstraint(
            "sequence >= 1",
            name="ck_ledger_entries_sequence",
        ),
        UniqueConstraint(
            "ledger_transaction_id",
            "sequence",
            name="uq_ledger_entries_transaction_sequence",
        ),
        Index(
            "ix_ledger_entries_account_created_at",
            "account_id",
            "created_at",
        ),
        Index(
            "ix_ledger_entries_account_transaction",
            "account_id",
            "ledger_transaction_id",
        ),
    )

    ledger_transaction_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("ledger_transactions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    account_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    ledger_transaction: Mapped[LedgerTransactionModel] = relationship(
        back_populates="entries",
        lazy="raise",
    )
    account: Mapped[AccountModel] = relationship(
        back_populates="ledger_entries",
        lazy="raise",
    )
