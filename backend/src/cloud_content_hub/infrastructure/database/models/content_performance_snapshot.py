"""Immutable ranked content performance snapshot model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Numeric,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import IMMUTABLE_UAC_CHECK
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.publication_target import (
        PublicationTarget,
    )
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class ContentPerformanceSnapshot(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Append-only projection of a publication target's content performance."""

    __tablename__ = "content_performance_snapshots"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "content_asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_content_performance_snapshots__asset",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "publication_target_id"],
            ["publication_targets.workspace_id", "publication_targets.id"],
            name="fk_content_performance_snapshots__target",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "reach IS NULL OR reach >= 0", name="ck_content_performance_snapshots__reach"
        ),
        CheckConstraint(
            "engagements IS NULL OR engagements >= 0",
            name="ck_content_performance_snapshots__engagements",
        ),
        CheckConstraint(
            "clicks IS NULL OR clicks >= 0", name="ck_content_performance_snapshots__clicks"
        ),
        CheckConstraint(
            "conversions IS NULL OR conversions >= 0",
            name="ck_content_performance_snapshots__conversions",
        ),
        CheckConstraint(
            "engagement_rate IS NULL OR engagement_rate >= 0",
            name="ck_content_performance_snapshots__engagement_rate",
        ),
        CheckConstraint(
            IMMUTABLE_UAC_CHECK,
            name="ck_content_performance_snapshots__immutable_uac",
        ),
        UniqueConstraint(
            "workspace_id", "id", name="uq_content_performance_snapshots__workspace_id_id"
        ),
        UniqueConstraint(
            "workspace_id",
            "publication_target_id",
            "snapshot_at",
            name="uq_content_performance_snapshots__target_time",
        ),
        Index(
            "ix_content_performance_snapshots__workspace_asset_time",
            "workspace_id",
            "content_asset_id",
            text("snapshot_at DESC"),
        ),
        Index(
            "ix_content_performance_snapshots__workspace_target",
            "workspace_id",
            "publication_target_id",
        ),
        {"comment": "Immutable ranked content-performance projection."},
    )

    content_asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    publication_target_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=False
    )
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reach: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    engagements: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    clicks: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    conversions: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    engagement_rate: Mapped[Decimal | None] = mapped_column(Numeric(12, 8), nullable=True)
    metrics: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="content_performance_snapshots",
        lazy="raise",
        overlaps="performance_snapshots",
    )
    content_asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="performance_snapshots",
        lazy="raise",
        overlaps="workspace",
    )
    publication_target: Mapped[PublicationTarget] = relationship(
        "PublicationTarget",
        back_populates="performance_snapshots",
        lazy="raise",
        overlaps="content_asset,performance_snapshots,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"ContentPerformanceSnapshot(id={self.id!r}, snapshot_at={self.snapshot_at!r})"
