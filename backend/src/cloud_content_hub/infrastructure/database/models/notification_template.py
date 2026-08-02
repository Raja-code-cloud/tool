"""Localized notification channel template model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import NotificationChannel
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.notification_type import NotificationType
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class NotificationTemplate(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Versioned localized template for a notification type and channel."""

    __tablename__ = "notification_templates"
    __table_args__ = (
        CheckConstraint(
            "channel IN ('in_app','email','webhook')",
            name="ck_notification_templates__channel",
        ),
        CheckConstraint("template_version > 0", name="ck_notification_templates__template_version"),
        Index(
            "uq_notification_templates__global_type_channel_locale_version",
            "notification_type_id",
            "channel",
            "locale",
            "template_version",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND workspace_id IS NULL"),
        ),
        Index(
            "uq_notification_templates__workspace_type_channel_locale_version",
            "workspace_id",
            "notification_type_id",
            "channel",
            "locale",
            "template_version",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND workspace_id IS NOT NULL"),
        ),
        Index(
            "ix_notification_templates__active_lookup",
            "notification_type_id",
            "channel",
            "locale",
            "is_active",
            postgresql_where=text("deleted_at IS NULL AND is_active"),
        ),
        {"comment": "Global or workspace-scoped localized notification rendering templates."},
    )

    notification_type_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("notification_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    workspace_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=True,
    )
    channel: Mapped[NotificationChannel] = mapped_column(Text, nullable=False)
    locale: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'en'"))
    template_version: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    notification_type: Mapped[NotificationType] = relationship(
        "NotificationType", back_populates="templates", lazy="raise"
    )
    workspace: Mapped[Workspace | None] = relationship(
        "Workspace", back_populates="notification_templates", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return (
            f"NotificationTemplate(id={self.id!r}, channel={self.channel!r}, "
            f"locale={self.locale!r})"
        )
