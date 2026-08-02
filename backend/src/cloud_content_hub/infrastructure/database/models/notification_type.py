"""Extensible notification event catalog model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY, CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import NotificationCategory
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.notification import Notification
    from cloud_content_hub.infrastructure.database.models.notification_preference import (
        NotificationPreference,
    )
    from cloud_content_hub.infrastructure.database.models.notification_template import (
        NotificationTemplate,
    )


class NotificationType(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Global catalog entry describing a notification event kind."""

    __tablename__ = "notification_types"
    __table_args__ = (
        CheckConstraint(
            "category IN ('transactional','product','security')",
            name="ck_notification_types__category",
        ),
        UniqueConstraint("code", name="uq_notification_types__code"),
        {"comment": "Extensible catalog of notification event kinds and default channels."},
    )

    code: Mapped[str] = mapped_column(CITEXT, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[NotificationCategory] = mapped_column(Text, nullable=False)
    default_channels: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
        server_default=text("'{}'::text[]"),
    )

    preferences: Mapped[list[NotificationPreference]] = relationship(
        "NotificationPreference", back_populates="notification_type", lazy="raise"
    )
    notifications: Mapped[list[Notification]] = relationship(
        "Notification", back_populates="notification_type", lazy="raise"
    )
    templates: Mapped[list[NotificationTemplate]] = relationship(
        "NotificationTemplate", back_populates="notification_type", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"NotificationType(id={self.id!r}, code={self.code!r})"
