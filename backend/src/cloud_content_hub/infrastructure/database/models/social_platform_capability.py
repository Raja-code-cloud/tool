"""Versioned social platform capability and limit record model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import CITEXT, JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.social_platform import SocialPlatform


class SocialPlatformCapability(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Append-only versioned platform capability and limit history."""

    __tablename__ = "social_platform_capabilities"
    __table_args__ = (
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_social_platform_capabilities__effective_interval",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_social_platform_capabilities__immutable_uac",
        ),
        UniqueConstraint(
            "platform_id",
            "capability_code",
            "effective_from",
            name="uq_social_platform_capabilities__platform_code_effective",
        ),
        Index("ix_social_platform_capabilities__created_at", "created_at", "id"),
        {"comment": "Immutable versioned social platform capability records."},
    )

    platform_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("social_platforms.id", ondelete="RESTRICT"),
        nullable=False,
    )
    capability_code: Mapped[str] = mapped_column(CITEXT(), nullable=False)
    supported: Mapped[bool] = mapped_column(Boolean, nullable=False)
    limit_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 6), nullable=True)
    unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    platform: Mapped[SocialPlatform] = relationship(
        "SocialPlatform", back_populates="capabilities", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"SocialPlatformCapability(id={self.id!r}, capability_code={self.capability_code!r})"
