"""Publication schedule with resolved publish time model."""

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
from cloud_content_hub.infrastructure.database.enums import (
    ScheduleAmbiguityPolicy,
    SchedulePriority,
    ScheduleState,
)
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.publication_status_history import (
        PublicationStatusHistory,
    )
    from cloud_content_hub.infrastructure.database.models.publication_target import (
        PublicationTarget,
    )
    from cloud_content_hub.infrastructure.database.models.publishing_job import PublishingJob
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class PublicationSchedule(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable authoritative requested and resolved publish schedule."""

    __tablename__ = "publication_schedules"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "publication_target_id"],
            ["publication_targets.workspace_id", "publication_targets.id"],
            name="fk_publication_schedules__publication_target",
            ondelete="RESTRICT",
        ),
        CheckConstraint("fold IS NULL OR fold IN (0, 1)", name="ck_publication_schedules__fold"),
        CheckConstraint(
            "ambiguity_policy IN ('reject','earlier','later')",
            name="ck_publication_schedules__ambiguity_policy",
        ),
        CheckConstraint(
            "state IN ('draft','scheduled','paused','dispatched','completed','cancelled','failed')",
            name="ck_publication_schedules__state",
        ),
        CheckConstraint(
            "priority IN ('low','normal','high')",
            name="ck_publication_schedules__priority",
        ),
        CheckConstraint("queue_order >= 0", name="ck_publication_schedules__queue_order"),
        UniqueConstraint("workspace_id", "id", name="uq_publication_schedules__workspace_id_id"),
        Index(
            "ix_publication_schedules__due",
            "scheduled_for",
            text("priority DESC"),
            "id",
            postgresql_include=["workspace_id", "publication_target_id"],
            postgresql_where=text("deleted_at IS NULL AND state = 'scheduled'"),
        ),
        Index(
            "ix_publication_schedules__workspace_calendar",
            "workspace_id",
            "scheduled_for",
            "id",
            postgresql_include=["state", "publication_target_id"],
            postgresql_where=text(
                "deleted_at IS NULL AND state IN "
                "('scheduled','paused','dispatched','completed','failed')"
            ),
        ),
        Index(
            "uq_publication_schedules__active_target",
            "workspace_id",
            "publication_target_id",
            unique=True,
            postgresql_where=text(
                "deleted_at IS NULL AND state IN ('scheduled','paused','dispatched')"
            ),
        ),
        Index(
            "ix_publication_schedules__workspace_target",
            "workspace_id",
            "publication_target_id",
        ),
        {"comment": "Authoritative requested and resolved publication schedule."},
    )

    publication_target_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=False
    )
    requested_local_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    time_zone: Mapped[str] = mapped_column(Text, nullable=False)
    fold: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ambiguity_policy: Mapped[ScheduleAmbiguityPolicy] = mapped_column(
        Text, nullable=False, server_default=text("'reject'")
    )
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    state: Mapped[ScheduleState] = mapped_column(
        Text, nullable=False, server_default=text("'draft'")
    )
    priority: Mapped[SchedulePriority] = mapped_column(
        Text, nullable=False, server_default=text("'normal'")
    )
    queue_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="publication_schedules", lazy="raise"
    )
    publication_target: Mapped[PublicationTarget] = relationship(
        "PublicationTarget",
        back_populates="schedules",
        lazy="raise",
        overlaps="workspace",
    )
    publishing_jobs: Mapped[list[PublishingJob]] = relationship(
        "PublishingJob", back_populates="schedule", lazy="raise"
    )
    status_history: Mapped[list[PublicationStatusHistory]] = relationship(
        "PublicationStatusHistory", back_populates="schedule", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"PublicationSchedule(id={self.id!r}, state={self.state!r})"
