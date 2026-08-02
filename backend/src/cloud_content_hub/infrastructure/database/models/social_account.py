"""Connected external social account model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import ConnectionStatus, HealthStatus
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.metric_observation import (
        MetricObservation,
    )
    from cloud_content_hub.infrastructure.database.models.oauth_token_vault import OAuthTokenVault
    from cloud_content_hub.infrastructure.database.models.publication_target import (
        PublicationTarget,
    )
    from cloud_content_hub.infrastructure.database.models.setting import Setting
    from cloud_content_hub.infrastructure.database.models.social_account_permission import (
        SocialAccountPermission,
    )
    from cloud_content_hub.infrastructure.database.models.social_account_setting import (
        SocialAccountSetting,
    )
    from cloud_content_hub.infrastructure.database.models.social_account_snapshot import (
        SocialAccountSnapshot,
    )
    from cloud_content_hub.infrastructure.database.models.social_platform import SocialPlatform
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class SocialAccount(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable connected external social account identity and health."""

    __tablename__ = "social_accounts"
    __table_args__ = (
        CheckConstraint(
            "connection_status IN ('connected','disconnected')",
            name="ck_social_accounts__connection_status",
        ),
        CheckConstraint(
            "health_status IN ('healthy','warning','error','needs_reauth')",
            name="ck_social_accounts__health_status",
        ),
        CheckConstraint(
            "followers_count IS NULL OR followers_count >= 0",
            name="ck_social_accounts__followers_count",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_social_accounts__workspace_id_id"),
        Index(
            "uq_social_accounts__workspace_platform_external_where_active",
            "workspace_id",
            "platform_id",
            "external_account_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_social_accounts__workspace_health",
            "workspace_id",
            "connection_status",
            "health_status",
            text("updated_at DESC"),
            text("id DESC"),
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_social_accounts__workspace_sync_due",
            "workspace_id",
            "last_sync_at",
            "id",
            postgresql_where=text("deleted_at IS NULL AND connection_status = 'connected'"),
        ),
        {"comment": "Connected external social account identity and health."},
    )

    platform_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("social_platforms.id", ondelete="RESTRICT"),
        nullable=False,
    )
    external_account_id: Mapped[str] = mapped_column(Text, nullable=False)
    account_name: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    username: Mapped[str | None] = mapped_column(Text, nullable=True)
    account_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    connection_status: Mapped[ConnectionStatus] = mapped_column(Text, nullable=False)
    health_status: Mapped[HealthStatus] = mapped_column(Text, nullable=False)
    publishing_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    default_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    time_zone: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'UTC'"))
    followers_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="social_accounts", lazy="raise"
    )
    platform: Mapped[SocialPlatform] = relationship(
        "SocialPlatform", back_populates="accounts", lazy="raise"
    )
    snapshots: Mapped[list[SocialAccountSnapshot]] = relationship(
        "SocialAccountSnapshot", back_populates="social_account", lazy="raise"
    )
    metric_observations: Mapped[list[MetricObservation]] = relationship(
        "MetricObservation",
        back_populates="social_account",
        lazy="raise",
        overlaps="content_asset,metric_observations,metric_observations,publication_target,workspace",
    )
    publication_targets: Mapped[list[PublicationTarget]] = relationship(
        "PublicationTarget",
        back_populates="social_account",
        lazy="raise",
        overlaps="content_version,generation_output,publication,publication_targets,publication_targets,targets,workspace",
    )
    oauth_token_vaults: Mapped[list[OAuthTokenVault]] = relationship(
        "OAuthTokenVault",
        back_populates="social_account",
        lazy="raise",
        overlaps="workspace",
    )
    permissions: Mapped[list[SocialAccountPermission]] = relationship(
        "SocialAccountPermission", back_populates="social_account", lazy="raise"
    )
    account_settings: Mapped[list[SocialAccountSetting]] = relationship(
        "SocialAccountSetting", back_populates="social_account", lazy="raise"
    )
    settings: Mapped[list[Setting]] = relationship(
        "Setting", back_populates="social_account", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"SocialAccount(id={self.id!r}, account_name={self.account_name!r})"
