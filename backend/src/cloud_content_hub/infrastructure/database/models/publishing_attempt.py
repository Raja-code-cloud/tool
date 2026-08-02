"""Immutable publishing provider attempt history model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import PublishingAttemptOutcome
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.publishing_job import PublishingJob
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class PublishingAttempt(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Append-only provider publishing attempt history."""

    __tablename__ = "publishing_attempts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "publishing_job_id"],
            ["publishing_jobs.workspace_id", "publishing_jobs.id"],
            name="fk_publishing_attempts__publishing_job",
            ondelete="RESTRICT",
        ),
        CheckConstraint("attempt_no > 0", name="ck_publishing_attempts__attempt_no"),
        CheckConstraint(
            check_in(PublishingAttemptOutcome, name="outcome"),
            name="ck_publishing_attempts__outcome",
        ),
        CheckConstraint(
            "http_status IS NULL OR (http_status >= 100 AND http_status <= 599)",
            name="ck_publishing_attempts__http_status",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_publishing_attempts__immutable_uac",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_publishing_attempts__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "publishing_job_id",
            "attempt_no",
            name="uq_publishing_attempts__job_attempt",
        ),
        Index(
            "ix_publishing_attempts__workspace_job_attempt",
            "workspace_id",
            "publishing_job_id",
            text("attempt_no DESC"),
        ),
        Index("ix_publishing_attempts__created_at", "created_at", "id"),
        {"comment": "Immutable provider publishing attempt history."},
    )

    publishing_job_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    outcome: Mapped[PublishingAttemptOutcome] = mapped_column(Text, nullable=False)
    provider_request_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_fragment: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="publishing_attempts", lazy="raise"
    )
    publishing_job: Mapped[PublishingJob] = relationship(
        "PublishingJob",
        back_populates="attempts",
        lazy="raise",
        overlaps="workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return (
            f"PublishingAttempt(id={self.id!r}, publishing_job_id="
            f"{self.publishing_job_id!r}, attempt_no={self.attempt_no!r})"
        )
