"""Per-channel notification delivery attempt model."""

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
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import (
    NotificationChannel,
    NotificationDeliveryStatus,
)
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.notification import Notification
    from cloud_content_hub.infrastructure.database.models.user import User
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class NotificationDelivery(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable per-channel delivery state for a notification recipient."""

    __tablename__ = "notification_deliveries"
    __table_args__ = (
        CheckConstraint(
            "channel IN ('in_app','email','webhook')",
            name="ck_notification_deliveries__channel",
        ),
        CheckConstraint(
            "status IN ('pending','sent','delivered','failed','suppressed')",
            name="ck_notification_deliveries__status",
        ),
        CheckConstraint("attempt_count >= 0", name="ck_notification_deliveries__attempt_count"),
        UniqueConstraint("workspace_id", "id", name="uq_notification_deliveries__workspace_id_id"),
        Index(
            "uq_notification_deliveries__notification_recipient_channel_where_active",
            "workspace_id",
            "notification_id",
            "recipient_user_id",
            "channel",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_notification_deliveries__due",
            "created_at",
            "id",
            postgresql_include=["workspace_id", "channel"],
            postgresql_where=text("deleted_at IS NULL AND status IN ('pending','failed')"),
        ),
        {"comment": "Per-channel delivery attempts and terminal status for notifications."},
    )

    notification_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("notifications.id", ondelete="RESTRICT"),
        nullable=False,
    )
    recipient_user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    channel: Mapped[NotificationChannel] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationDeliveryStatus] = mapped_column(Text, nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    provider_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="notification_deliveries", lazy="raise"
    )
    notification: Mapped[Notification] = relationship(
        "Notification", back_populates="deliveries", lazy="raise"
    )
    recipient: Mapped[User] = relationship(
        "User",
        foreign_keys=[recipient_user_id],
        back_populates="notification_deliveries",
        lazy="raise",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return (
            f"NotificationDelivery(id={self.id!r}, channel={self.channel!r}, "
            f"status={self.status!r})"
        )
