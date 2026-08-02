"""Recipient notification channel preference model."""

from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Text,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import NotificationChannel
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.notification_type import NotificationType
    from cloud_content_hub.infrastructure.database.models.user import User
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class NotificationPreference(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Per-recipient channel preference for a notification type."""

    __tablename__ = "notification_preferences"
    __table_args__ = (
        CheckConstraint(
            "channel IN ('in_app','email','webhook')",
            name="ck_notification_preferences__channel",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_notification_preferences__workspace_id_id"),
        Index(
            "uq_notification_preferences__workspace_user_type_channel_where_active",
            "workspace_id",
            "user_id",
            "notification_type_id",
            "channel",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Recipient channel preferences scoped to workspace and notification type."},
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    notification_type_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("notification_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    channel: Mapped[NotificationChannel] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    quiet_hours_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    quiet_hours_end: Mapped[time | None] = mapped_column(Time, nullable=True)
    time_zone: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'UTC'"))

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="notification_preferences", lazy="raise"
    )
    user: Mapped[User] = relationship(
        "User", foreign_keys=[user_id], back_populates="notification_preferences", lazy="raise"
    )
    notification_type: Mapped[NotificationType] = relationship(
        "NotificationType", back_populates="preferences", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"NotificationPreference(id={self.id!r}, channel={self.channel!r})"
