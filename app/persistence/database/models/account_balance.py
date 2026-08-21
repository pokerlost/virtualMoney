"""SQLAlchemy 2.x mapping persisted account balance projection."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.database import Base

if TYPE_CHECKING:
    from .account import AccountModel


class AccountBalanceModel(Base):
    """Persistence current state, rebuildable from immutable ledger entries."""

    __tablename__ = "account_balances"
    __table_args__ = (
        CheckConstraint(
            "held_balance_minor >= 0",
            name="ck_account_balances_held_non_negative",
        ),
        CheckConstraint(
            "version >= 0",
            name="ck_account_balances_version_non_negative",
        ),
    )

    account_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "accounts.id",
            name="fk_account_balances_account_id_accounts",
            ondelete="RESTRICT",
        ),
        primary_key=True,
    )
    posted_balance_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    held_balance_minor: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text("0"),
    )
    version: Mapped[int] = mapped_column(BigInteger, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    @property
    def available_balance_minor(self) -> int:
        """Return posted balance minus active held balance."""
        return self.posted_balance_minor - self.held_balance_minor

    account: Mapped[AccountModel] = relationship(
        back_populates="balance",
        lazy="raise",
    )
