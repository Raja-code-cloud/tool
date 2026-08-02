"""User-visible workspace notification instance model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import NotificationSeverity
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.notification_delivery import (
        NotificationDelivery,
    )
    from cloud_content_hub.infrastructure.database.models.notification_type import NotificationType
    from cloud_content_hub.infrastructure.database.models.user import User
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Notification(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable user-visible notification inbox item."""

    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "severity IN ('info','success','warning','error')",
            name="ck_notifications__severity",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_notifications__workspace_id_id"),
        Index(
            "uq_notifications__workspace_recipient_dedupe_where_active",
            "workspace_id",
            "recipient_user_id",
            "dedupe_key",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_notifications__workspace_recipient_unread",
            "workspace_id",
            "recipient_user_id",
            text("created_at DESC"),
            text("id DESC"),
            postgresql_where=text("deleted_at IS NULL AND read_at IS NULL"),
        ),
        Index(
            "ix_notifications__workspace_recipient_cursor",
            "workspace_id",
            "recipient_user_id",
            text("created_at DESC"),
            text("id DESC"),
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "User-visible notification instances with deduplicated inbox semantics."},
    )

    notification_type_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("notification_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    recipient_user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[NotificationSeverity] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    dedupe_key: Mapped[str] = mapped_column(Text, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="notifications", lazy="raise"
    )
    notification_type: Mapped[NotificationType] = relationship(
        "NotificationType", back_populates="notifications", lazy="raise"
    )
    recipient: Mapped[User] = relationship(
        "User", foreign_keys=[recipient_user_id], back_populates="notifications", lazy="raise"
    )
    deliveries: Mapped[list[NotificationDelivery]] = relationship(
        "NotificationDelivery", back_populates="notification", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Notification(id={self.id!r}, severity={self.severity!r})"
