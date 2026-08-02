"""Global internal user principal and profile model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Index, Text, text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import UserStatus
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.activity_log import ActivityLog
    from cloud_content_hub.infrastructure.database.models.audit_log import AuditLog
    from cloud_content_hub.infrastructure.database.models.data_export import DataExport
    from cloud_content_hub.infrastructure.database.models.external_identity import ExternalIdentity
    from cloud_content_hub.infrastructure.database.models.notification import Notification
    from cloud_content_hub.infrastructure.database.models.notification_delivery import (
        NotificationDelivery,
    )
    from cloud_content_hub.infrastructure.database.models.notification_preference import (
        NotificationPreference,
    )
    from cloud_content_hub.infrastructure.database.models.organization_membership import (
        OrganizationMembership,
    )
    from cloud_content_hub.infrastructure.database.models.setting import Setting
    from cloud_content_hub.infrastructure.database.models.user_session import UserSession
    from cloud_content_hub.infrastructure.database.models.workspace_membership import (
        WorkspaceMembership,
    )


class User(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Global internal principal with profile and lifecycle state only."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(check_in(UserStatus, name="status"), name="ck_users__status"),
        Index(
            "uq_users__email_where_active",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND email IS NOT NULL"),
        ),
        {"comment": "Global internal user principal; external subjects live elsewhere."},
    )

    email: Mapped[str | None] = mapped_column(CITEXT, nullable=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    avatar_object_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    locale: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'en'"))
    time_zone: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'UTC'"))
    status: Mapped[UserStatus] = mapped_column(
        Text, nullable=False, server_default=text("'active'")
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    external_identities: Mapped[list[ExternalIdentity]] = relationship(
        "ExternalIdentity",
        foreign_keys="ExternalIdentity.user_id",
        back_populates="user",
        lazy="raise",
    )
    user_sessions: Mapped[list[UserSession]] = relationship(
        "UserSession",
        foreign_keys="UserSession.user_id",
        back_populates="user",
        lazy="raise",
    )
    organization_memberships: Mapped[list[OrganizationMembership]] = relationship(
        "OrganizationMembership",
        foreign_keys="OrganizationMembership.user_id",
        back_populates="user",
        lazy="raise",
    )
    workspace_memberships: Mapped[list[WorkspaceMembership]] = relationship(
        "WorkspaceMembership",
        foreign_keys="[WorkspaceMembership.user_id]",
        back_populates="user",
        lazy="raise",
    )
    activity_logs: Mapped[list[ActivityLog]] = relationship(
        "ActivityLog",
        foreign_keys="ActivityLog.actor_id",
        back_populates="actor",
        lazy="raise",
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        "AuditLog",
        foreign_keys="AuditLog.actor_user_id",
        back_populates="actor_user",
        lazy="raise",
    )

    data_exports: Mapped[list[DataExport]] = relationship(
        "DataExport",
        foreign_keys="DataExport.requested_by",
        back_populates="requester",
        lazy="raise",
    )
    notifications: Mapped[list[Notification]] = relationship(
        "Notification",
        foreign_keys="Notification.recipient_user_id",
        back_populates="recipient",
        lazy="raise",
    )
    notification_deliveries: Mapped[list[NotificationDelivery]] = relationship(
        "NotificationDelivery",
        foreign_keys="NotificationDelivery.recipient_user_id",
        back_populates="recipient",
        lazy="raise",
    )
    notification_preferences: Mapped[list[NotificationPreference]] = relationship(
        "NotificationPreference",
        foreign_keys="NotificationPreference.user_id",
        back_populates="user",
        lazy="raise",
    )
    settings: Mapped[list[Setting]] = relationship(
        "Setting",
        foreign_keys="Setting.user_id",
        back_populates="user",
        lazy="raise",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"User(id={self.id!r}, status={self.status!r})"
