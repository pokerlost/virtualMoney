"""SQLAlchemy 2.x mapping for an internal financial asset."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, SmallInteger, String, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import AssetStatus
from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin


class AssetModel(TimestampMixin, UUIDModel):
    """Persistence representation of Asset metadata without balance or blockchain fields."""

    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint(
            "code ~ '^[A-Z][A-Z0-9_]{1,15}$'",
            name="ck_assets_code_format",
        ),
        CheckConstraint(
            "char_length(btrim(name)) BETWEEN 1 AND 128",
            name="ck_assets_name_not_blank",
        ),
        CheckConstraint(
            "minor_unit_scale BETWEEN 0 AND 8",
            name="ck_assets_minor_unit_scale",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_assets_status",
        ),
        UniqueConstraint("code", name="uq_assets_code"),
    )

    code: Mapped[str] = mapped_column(String(16), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    minor_unit_scale: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    status: Mapped[AssetStatus] = mapped_column(
        SqlEnum(
            AssetStatus,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            length=16,
        ),
        nullable=False,
    )
