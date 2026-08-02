"""User-facing workspace activity feed model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.user import User
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class ActivityLog(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable-retention activity item displayed in a workspace feed."""

    __tablename__ = "activity_logs"
    __table_args__ = (
        Index(
            "ix_activity_logs__workspace_cursor",
            "workspace_id",
            text("occurred_at DESC"),
            text("id DESC"),
            postgresql_where=text("deleted_at IS NULL AND hidden_at IS NULL"),
        ),
        {"comment": "User-facing recent activity; not compliance evidence."},
    )

    actor_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    activity_type: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    hidden_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="activity_logs", lazy="raise"
    )
    actor: Mapped[User | None] = relationship(
        "User", foreign_keys=[actor_id], back_populates="activity_logs", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"ActivityLog(id={self.id!r}, activity_type={self.activity_type!r})"
