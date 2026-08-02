"""Transactional outbox event model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.organization import Organization
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class OutboxEvent(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Immutable integration event persisted with its originating transaction."""

    __tablename__ = "outbox_events"
    __table_args__ = (
        CheckConstraint("event_version > 0", name="outbox_events_event_version_positive"),
        CheckConstraint("attempt_count >= 0", name="outbox_events_attempt_count_nonnegative"),
        CheckConstraint(
            "workspace_id IS NOT NULL OR organization_id IS NOT NULL OR aggregate_type = 'global'",
            name="outbox_events_scope",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="outbox_events_immutable_shape",
        ),
        Index(
            "ix_outbox_events__publish_due",
            "available_at",
            "id",
            postgresql_where=text("published_at IS NULL"),
        ),
        Index(
            "ix_outbox_events__aggregate",
            "aggregate_type",
            "aggregate_id",
            "occurred_at",
            "id",
        ),
        Index(
            "brin_outbox_events__occurred_at",
            "occurred_at",
            postgresql_using="brin",
            postgresql_with={"pages_per_range": 64},
        ),
        {"comment": "Redacted, versioned transactional integration events."},
    )

    workspace_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=True,
    )
    organization_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=True,
    )
    aggregate_type: Mapped[str] = mapped_column(Text, nullable=False)
    aggregate_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    event_version: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    headers: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace | None] = relationship(
        "Workspace", back_populates="outbox_events", lazy="raise"
    )
    organization: Mapped[Organization | None] = relationship(
        "Organization", back_populates="outbox_events", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"OutboxEvent(id={self.id!r}, event_type={self.event_type!r})"
