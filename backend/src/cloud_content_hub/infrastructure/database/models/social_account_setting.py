"""Social account publishing defaults model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Boolean, ForeignKeyConstraint, Index, Text, UniqueConstraint, text
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
    from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class SocialAccountSetting(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable publishing defaults for a connected social account."""

    __tablename__ = "social_account_settings"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "social_account_id"],
            ["social_accounts.workspace_id", "social_accounts.id"],
            name="fk_social_account_settings__social_account",
            ondelete="RESTRICT",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_social_account_settings__workspace_id_id"),
        Index(
            "uq_social_account_settings__workspace_account_where_active",
            "workspace_id",
            "social_account_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_social_account_settings__workspace_account",
            "workspace_id",
            "social_account_id",
        ),
        {"comment": "Publishing defaults and feature toggles for social accounts."},
    )

    social_account_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    visibility: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtag_strategy: Mapped[str | None] = mapped_column(Text, nullable=True)
    auto_publish: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    ai_optimization: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    auto_schedule: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    url_tracking: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    provider_defaults: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="social_account_settings",
        lazy="raise",
        overlaps="account_settings",
    )
    social_account: Mapped[SocialAccount] = relationship(
        "SocialAccount",
        back_populates="account_settings",
        lazy="raise",
        overlaps="workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"SocialAccountSetting(id={self.id!r}, social_account_id={self.social_account_id!r})"
