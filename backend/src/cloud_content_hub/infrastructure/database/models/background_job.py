"""Durable non-publishing background job model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import JobState
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class BackgroundJob(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Mutable durable work item for non-publishing worker queues."""

    __tablename__ = "background_jobs"
    __table_args__ = (
        CheckConstraint(
            "queue_name IN ('ai','media','notification','maintenance')",
            name="background_jobs_queue_name",
        ),
        CheckConstraint(
            "state IN "
            "('queued','leased','running','retry_wait','succeeded','failed',"
            "'dead_lettered','cancelled')",
            name="background_jobs_state",
        ),
        CheckConstraint("attempt_count >= 0", name="background_jobs_attempt_count_nonnegative"),
        CheckConstraint("max_attempts > 0", name="background_jobs_max_attempts_positive"),
        CheckConstraint(
            "attempt_count <= max_attempts",
            name="background_jobs_attempts_within_max",
        ),
        Index(
            "uq_background_jobs__scope_type_key_where_active",
            "workspace_id",
            "job_type",
            "idempotency_key",
            unique=True,
            postgresql_nulls_not_distinct=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_background_jobs__claim",
            "available_at",
            text("priority DESC"),
            "id",
            postgresql_include=["workspace_id", "queue_name"],
            postgresql_where=text("deleted_at IS NULL AND state IN ('queued','retry_wait')"),
        ),
        Index(
            "ix_background_jobs__expired_lease",
            "leased_until",
            "id",
            postgresql_where=text("deleted_at IS NULL AND state IN ('leased','running')"),
        ),
        {"comment": "Durable non-publishing work with bounded retries and leases."},
    )

    workspace_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=True,
    )
    job_type: Mapped[str] = mapped_column(Text, nullable=False)
    queue_name: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[JobState] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"))
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("5"))
    lease_owner: Mapped[str | None] = mapped_column(Text, nullable=True)
    leased_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column("error_message", Text, nullable=True)

    workspace: Mapped[Workspace | None] = relationship(
        "Workspace", back_populates="background_jobs", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"BackgroundJob(id={self.id!r}, job_type={self.job_type!r}, state={self.state!r})"
