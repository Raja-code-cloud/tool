"""Immutable normalized analytics observation model."""

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
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.metric_definition import MetricDefinition
    from cloud_content_hub.infrastructure.database.models.publication_target import (
        PublicationTarget,
    )
    from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class MetricObservation(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Append-only raw metric fact deduplicated by provider fingerprint."""

    __tablename__ = "metric_observations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "social_account_id"],
            ["social_accounts.workspace_id", "social_accounts.id"],
            name="fk_metric_observations__social_account",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "publication_target_id"],
            ["publication_targets.workspace_id", "publication_targets.id"],
            name="fk_metric_observations__publication_target",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "content_asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_metric_observations__content_asset",
            ondelete="RESTRICT",
        ),
        CheckConstraint("bucket_end > bucket_start", name="ck_metric_observations__bucket"),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_metric_observations__immutable_uac",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_metric_observations__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "metric_definition_id",
            "source_fingerprint",
            name="uq_metric_observations__workspace_metric_fingerprint",
        ),
        Index(
            "ix_metric_observations__workspace_metric_time",
            "workspace_id",
            "metric_definition_id",
            text("observed_at DESC"),
            text("id DESC"),
        ),
        Index(
            "ix_metric_observations__workspace_publication_target_metric_time",
            "workspace_id",
            "publication_target_id",
            "metric_definition_id",
            text("observed_at DESC"),
        ),
        Index(
            "ix_metric_observations__workspace_social_account_metric_time",
            "workspace_id",
            "social_account_id",
            "metric_definition_id",
            text("observed_at DESC"),
        ),
        Index(
            "brin_metric_observations__observed_at",
            "observed_at",
            postgresql_using="brin",
            postgresql_with={"pages_per_range": 64},
        ),
        {"comment": "Immutable raw normalized time-series analytics facts."},
    )

    metric_definition_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("metric_definitions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    social_account_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    publication_target_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    content_asset_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    bucket_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    bucket_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    is_estimated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    source_fingerprint: Mapped[bytes] = mapped_column(nullable=False)
    provider_fragment: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="metric_observations",
        lazy="raise",
        overlaps="metric_observations",
    )
    metric_definition: Mapped[MetricDefinition] = relationship(
        "MetricDefinition", back_populates="observations", lazy="raise"
    )
    social_account: Mapped[SocialAccount | None] = relationship(
        "SocialAccount",
        back_populates="metric_observations",
        lazy="raise",
        overlaps="metric_observations,workspace",
    )
    publication_target: Mapped[PublicationTarget | None] = relationship(
        "PublicationTarget",
        back_populates="metric_observations",
        lazy="raise",
        overlaps="metric_observations,social_account,workspace",
    )
    content_asset: Mapped[ContentAsset | None] = relationship(
        "ContentAsset",
        back_populates="metric_observations",
        lazy="raise",
        overlaps="publication_target,social_account,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"MetricObservation(id={self.id!r}, observed_at={self.observed_at!r})"
