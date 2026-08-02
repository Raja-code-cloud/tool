"""Consumer inbox deduplication model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, LargeBinary, Text, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class InboxMessage(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Immutable record proving a consumer observed a message identifier."""

    __tablename__ = "inbox_messages"
    __table_args__ = (
        CheckConstraint(
            "outcome IS NULL OR outcome IN ('processed','ignored','failed')",
            name="inbox_messages_outcome",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="inbox_messages_immutable_shape",
        ),
        Index(
            "uq_inbox_messages__consumer_message",
            "consumer_name",
            "message_id",
            unique=True,
        ),
        Index(
            "ix_inbox_messages__retention",
            "processed_at",
            "id",
            postgresql_where=text("processed_at IS NOT NULL"),
        ),
        {"comment": "Immutable at-least-once consumer deduplication evidence."},
    )

    workspace_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=True,
    )
    consumer_name: Mapped[str] = mapped_column(Text, nullable=False)
    message_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    workspace: Mapped[Workspace | None] = relationship(
        "Workspace", back_populates="inbox_messages", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"InboxMessage(id={self.id!r}, consumer_name={self.consumer_name!r})"
