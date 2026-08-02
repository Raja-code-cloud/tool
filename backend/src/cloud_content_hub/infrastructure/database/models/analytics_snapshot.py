"""Immutable workspace analytics aggregate snapshot model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class AnalyticsSnapshot(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Append-only dashboard aggregate cache with freshness metadata."""

    __tablename__ = "analytics_snapshots"
    __table_args__ = (
        CheckConstraint(
            "snapshot_type IN ('workspace_kpi','platform_comparison','growth_trend',"
            "'publishing_frequency')",
            name="ck_analytics_snapshots__snapshot_type",
        ),
        CheckConstraint("period_end > period_start", name="ck_analytics_snapshots__period"),
        CheckConstraint("methodology_version > 0", name="ck_analytics_snapshots__methodology"),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_analytics_snapshots__immutable_uac",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_analytics_snapshots__workspace_id_id"),
        Index(
            "uq_analytics_snapshots__identity",
            "workspace_id",
            "snapshot_type",
            "period_start",
            "period_end",
            "methodology_version",
            text("md5(dimensions::text)"),
            unique=True,
        ),
        Index(
            "ix_analytics_snapshots__workspace_type_period_end",
            "workspace_id",
            "snapshot_type",
            text("period_end DESC"),
            text("id DESC"),
        ),
        {"comment": "Immutable dashboard aggregate cache with explicit methodology."},
    )

    snapshot_type: Mapped[str] = mapped_column(Text, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    time_zone: Mapped[str] = mapped_column(Text, nullable=False)
    dimensions: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    fresh_through: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    methodology_version: Mapped[int] = mapped_column(Integer, nullable=False)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="analytics_snapshots", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"AnalyticsSnapshot(id={self.id!r}, snapshot_type={self.snapshot_type!r})"
