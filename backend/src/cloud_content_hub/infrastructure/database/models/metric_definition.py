"""Extensible global analytics metric catalog model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.metric_observation import (
        MetricObservation,
    )
    from cloud_content_hub.infrastructure.database.models.social_platform import SocialPlatform


class MetricDefinition(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Versioned definition of a normalized analytics metric."""

    __tablename__ = "metric_definitions"
    __table_args__ = (
        CheckConstraint(
            "aggregation IN ('sum','last','max','min','average','ratio')",
            name="ck_metric_definitions__aggregation",
        ),
        CheckConstraint(
            "value_kind IN ('integer','decimal','percentage','currency')",
            name="ck_metric_definitions__value_kind",
        ),
        CheckConstraint(
            "methodology_version > 0",
            name="ck_metric_definitions__methodology_version_positive",
        ),
        UniqueConstraint(
            "code",
            "methodology_version",
            "platform_id",
            name="uq_metric_definitions__code_version_platform",
            postgresql_nulls_not_distinct=True,
        ),
        {"comment": "Versioned, extensible semantics for normalized analytics metrics."},
    )

    code: Mapped[str] = mapped_column(CITEXT, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str] = mapped_column(Text, nullable=False)
    aggregation: Mapped[str] = mapped_column(Text, nullable=False)
    value_kind: Mapped[str] = mapped_column(Text, nullable=False)
    methodology_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    platform_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("social_platforms.id", ondelete="RESTRICT"),
        nullable=True,
    )

    platform: Mapped[SocialPlatform | None] = relationship(
        "SocialPlatform", back_populates="metric_definitions", lazy="raise"
    )
    observations: Mapped[list[MetricObservation]] = relationship(
        "MetricObservation", back_populates="metric_definition", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return (
            f"MetricDefinition(id={self.id!r}, code={self.code!r}, "
            f"methodology_version={self.methodology_version!r})"
        )
