"""Durable publishing job execution model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import JobState
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.job_lease import JobLease
    from cloud_content_hub.infrastructure.database.models.publication_schedule import (
        PublicationSchedule,
    )
    from cloud_content_hub.infrastructure.database.models.publication_status_history import (
        PublicationStatusHistory,
    )
    from cloud_content_hub.infrastructure.database.models.publication_target import (
        PublicationTarget,
    )
    from cloud_content_hub.infrastructure.database.models.publishing_attempt import (
        PublishingAttempt,
    )
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class PublishingJob(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable durable publish execution work item."""

    __tablename__ = "publishing_jobs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "schedule_id"],
            ["publication_schedules.workspace_id", "publication_schedules.id"],
            name="fk_publishing_jobs__schedule",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "target_id"],
            ["publication_targets.workspace_id", "publication_targets.id"],
            name="fk_publishing_jobs__target",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "state IN "
            "('queued','leased','running','retry_wait','succeeded','failed',"
            "'dead_lettered','cancelled')",
            name="ck_publishing_jobs__state",
        ),
        CheckConstraint("attempt_count >= 0", name="ck_publishing_jobs__attempt_count"),
        CheckConstraint("max_attempts > 0", name="ck_publishing_jobs__max_attempts"),
        CheckConstraint(
            "attempt_count <= max_attempts",
            name="ck_publishing_jobs__attempts_within_max",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_publishing_jobs__workspace_id_id"),
        Index(
            "uq_publishing_jobs__workspace_idempotency",
            "workspace_id",
            "idempotency_key",
            unique=True,
        ),
        Index(
            "ix_publishing_jobs__claim",
            "available_at",
            text("priority DESC"),
            "id",
            postgresql_include=["workspace_id"],
            postgresql_where=text("deleted_at IS NULL AND state IN ('queued','retry_wait')"),
        ),
        Index(
            "ix_publishing_jobs__workspace_status_cursor",
            "workspace_id",
            "state",
            text("updated_at DESC"),
            text("id DESC"),
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_publishing_jobs__workspace_target", "workspace_id", "target_id"),
        Index("ix_publishing_jobs__workspace_schedule", "workspace_id", "schedule_id"),
        {"comment": "Durable publish execution with bounded retries."},
    )

    schedule_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    target_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    state: Mapped[JobState] = mapped_column(Text, nullable=False, server_default=text("'queued'"))
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"))
    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("5"))
    last_error_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="publishing_jobs",
        lazy="raise",
        overlaps="publishing_jobs,publishing_jobs",
    )
    schedule: Mapped[PublicationSchedule] = relationship(
        "PublicationSchedule",
        back_populates="publishing_jobs",
        lazy="raise",
        overlaps="publishing_jobs,workspace",
    )
    publication_target: Mapped[PublicationTarget] = relationship(
        "PublicationTarget",
        back_populates="publishing_jobs",
        lazy="raise",
        overlaps="publishing_jobs,schedule,workspace",
    )
    attempts: Mapped[list[PublishingAttempt]] = relationship(
        "PublishingAttempt",
        back_populates="publishing_job",
        lazy="raise",
        overlaps="workspace",
    )
    leases: Mapped[list[JobLease]] = relationship(
        "JobLease",
        back_populates="publishing_job",
        lazy="raise",
        overlaps="workspace",
    )
    status_history: Mapped[list[PublicationStatusHistory]] = relationship(
        "PublicationStatusHistory",
        back_populates="job",
        lazy="raise",
        overlaps="publication_target,schedule,status_history,status_history,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"PublishingJob(id={self.id!r}, state={self.state!r})"
