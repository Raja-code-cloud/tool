"""Append-only publication status timeline model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import PublicationStatusHistoryType
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.publication_schedule import (
        PublicationSchedule,
    )
    from cloud_content_hub.infrastructure.database.models.publication_target import (
        PublicationTarget,
    )
    from cloud_content_hub.infrastructure.database.models.publishing_job import PublishingJob
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class PublicationStatusHistory(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Append-only publication target status timeline."""

    __tablename__ = "publication_status_history"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "publication_target_id"],
            ["publication_targets.workspace_id", "publication_targets.id"],
            name="fk_publication_status_history__publication_target",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "schedule_id"],
            ["publication_schedules.workspace_id", "publication_schedules.id"],
            name="fk_publication_status_history__schedule",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "job_id"],
            ["publishing_jobs.workspace_id", "publishing_jobs.id"],
            name="fk_publication_status_history__job",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "state_type IN ('approval','schedule','job','provider')",
            name="ck_publication_status_history__state_type",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_publication_status_history__immutable_uac",
        ),
        UniqueConstraint(
            "workspace_id", "id", name="uq_publication_status_history__workspace_id_id"
        ),
        Index(
            "ix_publication_status_history__workspace_target_time",
            "workspace_id",
            "publication_target_id",
            text("occurred_at DESC"),
            text("id DESC"),
        ),
        Index("ix_publication_status_history__occurred_at", "occurred_at", "id"),
        {"comment": "Append-only publication target status timeline."},
    )

    publication_target_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=False
    )
    schedule_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    job_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    state_type: Mapped[PublicationStatusHistoryType] = mapped_column(Text, nullable=False)
    from_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    to_state: Mapped[str] = mapped_column(Text, nullable=False)
    reason_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="publication_status_history",
        lazy="raise",
        overlaps="status_history",
    )
    publication_target: Mapped[PublicationTarget] = relationship(
        "PublicationTarget",
        back_populates="status_history",
        lazy="raise",
        overlaps="status_history,workspace",
    )
    schedule: Mapped[PublicationSchedule | None] = relationship(
        "PublicationSchedule",
        back_populates="status_history",
        lazy="raise",
        overlaps="publication_target,workspace",
    )
    job: Mapped[PublishingJob | None] = relationship(
        "PublishingJob",
        back_populates="status_history",
        lazy="raise",
        overlaps="publication_target,schedule,status_history,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return (
            f"PublicationStatusHistory(id={self.id!r}, state_type={self.state_type!r}, "
            f"to_state={self.to_state!r})"
        )
