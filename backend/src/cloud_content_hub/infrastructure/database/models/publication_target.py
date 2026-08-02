"""Publication target account and platform rendition model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import ApprovalState
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.ai_generation_output import (
        AIGenerationOutput,
    )
    from cloud_content_hub.infrastructure.database.models.content_performance_snapshot import (
        ContentPerformanceSnapshot,
    )
    from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
    from cloud_content_hub.infrastructure.database.models.metric_observation import (
        MetricObservation,
    )
    from cloud_content_hub.infrastructure.database.models.publication import Publication
    from cloud_content_hub.infrastructure.database.models.publication_schedule import (
        PublicationSchedule,
    )
    from cloud_content_hub.infrastructure.database.models.publication_status_history import (
        PublicationStatusHistory,
    )
    from cloud_content_hub.infrastructure.database.models.publishing_job import PublishingJob
    from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
    from cloud_content_hub.infrastructure.database.models.social_platform import SocialPlatform
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class PublicationTarget(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable per-account platform rendition within a publication."""

    __tablename__ = "publication_targets"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "publication_id"],
            ["publications.workspace_id", "publications.id"],
            name="fk_publication_targets__publication",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "social_account_id"],
            ["social_accounts.workspace_id", "social_accounts.id"],
            name="fk_publication_targets__social_account",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "content_version_id"],
            ["content_versions.workspace_id", "content_versions.id"],
            name="fk_publication_targets__content_version",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "generation_output_id"],
            ["ai_generation_outputs.workspace_id", "ai_generation_outputs.id"],
            name="fk_publication_targets__generation_output",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "approval_state IN ('pending','approved','rejected','changes_requested','cancelled')",
            name="ck_publication_targets__approval_state",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_publication_targets__workspace_id_id"),
        Index(
            "uq_publication_targets__workspace_publication_account_where_active",
            "workspace_id",
            "publication_id",
            "social_account_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_publication_targets__workspace_publication",
            "workspace_id",
            "publication_id",
            "id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_publication_targets__workspace_account_published",
            "workspace_id",
            "social_account_id",
            text("published_at DESC"),
            text("id DESC"),
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_publication_targets__external_post",
            "platform_id",
            "external_post_id",
            postgresql_where=text("external_post_id IS NOT NULL"),
        ),
        {"comment": "Per-account platform rendition within a publication."},
    )

    publication_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    social_account_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    platform_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("social_platforms.id", ondelete="RESTRICT"),
        nullable=False,
    )
    content_version_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    generation_output_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    approval_state: Mapped[ApprovalState] = mapped_column(Text, nullable=False)
    external_post_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_post_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="publication_targets",
        lazy="raise",
        overlaps="publication_targets,publication_targets,targets",
    )
    publication: Mapped[Publication] = relationship(
        "Publication",
        back_populates="targets",
        lazy="raise",
        overlaps="publication_targets,publication_targets,workspace",
    )
    social_account: Mapped[SocialAccount] = relationship(
        "SocialAccount",
        back_populates="publication_targets",
        lazy="raise",
        overlaps="publication,publication_targets,publication_targets,targets,workspace",
    )
    platform: Mapped[SocialPlatform] = relationship(
        "SocialPlatform", back_populates="publication_targets", lazy="raise"
    )
    content_version: Mapped[ContentVersion] = relationship(
        "ContentVersion",
        back_populates="publication_targets",
        lazy="raise",
        overlaps="publication,publication_targets,social_account,targets,workspace",
    )
    generation_output: Mapped[AIGenerationOutput | None] = relationship(
        "AIGenerationOutput",
        back_populates="publication_targets",
        lazy="raise",
        overlaps="content_version,publication,publication_targets,social_account,targets,workspace",
    )
    schedules: Mapped[list[PublicationSchedule]] = relationship(
        "PublicationSchedule",
        back_populates="publication_target",
        lazy="raise",
        overlaps="workspace",
    )
    publishing_jobs: Mapped[list[PublishingJob]] = relationship(
        "PublishingJob",
        back_populates="publication_target",
        lazy="raise",
        overlaps="publishing_jobs",
    )
    status_history: Mapped[list[PublicationStatusHistory]] = relationship(
        "PublicationStatusHistory",
        back_populates="publication_target",
        lazy="raise",
        overlaps="job,schedule,status_history,workspace",
    )
    metric_observations: Mapped[list[MetricObservation]] = relationship(
        "MetricObservation",
        back_populates="publication_target",
        lazy="raise",
        overlaps="content_asset,metric_observations,social_account,workspace",
    )
    performance_snapshots: Mapped[list[ContentPerformanceSnapshot]] = relationship(
        "ContentPerformanceSnapshot",
        back_populates="publication_target",
        lazy="raise",
        overlaps="content_asset,performance_snapshots,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"PublicationTarget(id={self.id!r}, approval_state={self.approval_state!r})"
