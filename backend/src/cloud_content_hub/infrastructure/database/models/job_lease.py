"""Short-lived publishing job lease model."""

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
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.publishing_job import PublishingJob
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class JobLease(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Append-only short-lived worker claim and heartbeat for publishing jobs."""

    __tablename__ = "job_leases"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "publishing_job_id"],
            ["publishing_jobs.workspace_id", "publishing_jobs.id"],
            name="fk_job_leases__publishing_job",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_job_leases__immutable_uac",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_job_leases__workspace_id_id"),
        Index("uq_job_leases__lease_token", "lease_token", unique=True),
        Index("ix_job_leases__expired", "leased_until", "id"),
        Index("ix_job_leases__workspace_job", "workspace_id", "publishing_job_id"),
        Index("ix_job_leases__created_at", "created_at", "id"),
        {"comment": "Short-lived publishing job worker leases and heartbeats."},
    )

    publishing_job_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    lease_owner: Mapped[str] = mapped_column(Text, nullable=False)
    lease_token: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    leased_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="job_leases", lazy="raise"
    )
    publishing_job: Mapped[PublishingJob] = relationship(
        "PublishingJob",
        back_populates="leases",
        lazy="raise",
        overlaps="workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"JobLease(id={self.id!r}, publishing_job_id={self.publishing_job_id!r})"
