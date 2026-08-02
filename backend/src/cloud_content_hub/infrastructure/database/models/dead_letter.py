"""Terminal failed work dead-letter queue model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import (
    DeadLetterReplayState,
    DeadLetterSourceType,
)
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class DeadLetter(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable terminal failed work envelope with controlled replay state."""

    __tablename__ = "dead_letters"
    __table_args__ = (
        CheckConstraint(
            "source_type IN ('publishing_job','notification','outbox','webhook','background_job')",
            name="ck_dead_letters__source_type",
        ),
        CheckConstraint(
            "replay_state IN ('pending','replayed','discarded')",
            name="ck_dead_letters__replay_state",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_dead_letters__workspace_id_id"),
        Index(
            "uq_dead_letters__workspace_source_where_active",
            "workspace_id",
            "source_type",
            "source_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_dead_letters__workspace_pending",
            "workspace_id",
            "failed_at",
            "id",
            postgresql_where=text("deleted_at IS NULL AND replay_state = 'pending'"),
        ),
        {"comment": "Terminal failed work with redacted payload and replay control."},
    )

    source_type: Mapped[DeadLetterSourceType] = mapped_column(Text, nullable=False)
    source_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    reason_code: Mapped[str] = mapped_column(Text, nullable=False)
    reason_message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    failed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    replay_state: Mapped[DeadLetterReplayState] = mapped_column(
        Text, nullable=False, server_default=text("'pending'")
    )
    replayed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="dead_letters", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"DeadLetter(id={self.id!r}, source_type={self.source_type!r})"
