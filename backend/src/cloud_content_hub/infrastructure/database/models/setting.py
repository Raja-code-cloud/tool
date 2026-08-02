"""Scoped setting override and inheritance model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import SettingScopeType
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.organization import Organization
    from cloud_content_hub.infrastructure.database.models.project import Project
    from cloud_content_hub.infrastructure.database.models.setting_definition import (
        SettingDefinition,
    )
    from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
    from cloud_content_hub.infrastructure.database.models.user import User
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Setting(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Scoped override for a setting definition with inheritance semantics."""

    __tablename__ = "settings"
    __table_args__ = (
        CheckConstraint(
            "scope_type IN ('organization','workspace','user','project','social_account')",
            name="ck_settings__scope_type",
        ),
        CheckConstraint(
            "("
            "(scope_type = 'organization' AND organization_id IS NOT NULL "
            "AND workspace_id IS NULL AND user_id IS NULL "
            "AND project_id IS NULL AND social_account_id IS NULL)"
            " OR "
            "(scope_type = 'workspace' AND workspace_id IS NOT NULL "
            "AND organization_id IS NULL AND user_id IS NULL "
            "AND project_id IS NULL AND social_account_id IS NULL)"
            " OR "
            "(scope_type = 'user' AND workspace_id IS NOT NULL AND user_id IS NOT NULL "
            "AND organization_id IS NULL AND project_id IS NULL AND social_account_id IS NULL)"
            " OR "
            "(scope_type = 'project' AND workspace_id IS NOT NULL AND project_id IS NOT NULL "
            "AND organization_id IS NULL AND user_id IS NULL AND social_account_id IS NULL)"
            " OR "
            "(scope_type = 'social_account' AND workspace_id IS NOT NULL "
            "AND social_account_id IS NOT NULL "
            "AND organization_id IS NULL AND user_id IS NULL AND project_id IS NULL)"
            ")",
            name="ck_settings__scope_target",
        ),
        Index(
            "uq_settings__organization_definition",
            "organization_id",
            "definition_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND scope_type = 'organization'"),
        ),
        Index(
            "uq_settings__workspace_definition",
            "workspace_id",
            "definition_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND scope_type = 'workspace'"),
        ),
        Index(
            "uq_settings__user_definition",
            "workspace_id",
            "user_id",
            "definition_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND scope_type = 'user'"),
        ),
        Index(
            "uq_settings__project_definition",
            "workspace_id",
            "project_id",
            "definition_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND scope_type = 'project'"),
        ),
        Index(
            "uq_settings__social_account_definition",
            "workspace_id",
            "social_account_id",
            "definition_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND scope_type = 'social_account'"),
        ),
        Index(
            "ix_settings__organization_definition",
            "organization_id",
            "definition_id",
            postgresql_where=text("deleted_at IS NULL AND scope_type = 'organization'"),
        ),
        Index(
            "ix_settings__workspace_definition",
            "workspace_id",
            "definition_id",
            postgresql_where=text("deleted_at IS NULL AND scope_type = 'workspace'"),
        ),
        Index(
            "ix_settings__user_definition",
            "workspace_id",
            "user_id",
            "definition_id",
            postgresql_where=text("deleted_at IS NULL AND scope_type = 'user'"),
        ),
        Index(
            "ix_settings__project_definition",
            "workspace_id",
            "project_id",
            "definition_id",
            postgresql_where=text("deleted_at IS NULL AND scope_type = 'project'"),
        ),
        Index(
            "ix_settings__social_account_definition",
            "workspace_id",
            "social_account_id",
            "definition_id",
            postgresql_where=text("deleted_at IS NULL AND scope_type = 'social_account'"),
        ),
        {"comment": "Scoped setting overrides resolved from specific to general."},
    )

    workspace_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=True,
    )
    organization_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=True,
    )
    user_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    project_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=True,
    )
    social_account_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("social_accounts.id", ondelete="RESTRICT"),
        nullable=True,
    )
    definition_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("setting_definitions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    scope_type: Mapped[SettingScopeType] = mapped_column(Text, nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    workspace: Mapped[Workspace | None] = relationship(
        "Workspace", back_populates="settings", lazy="raise"
    )
    organization: Mapped[Organization | None] = relationship(
        "Organization", back_populates="settings", lazy="raise"
    )
    user: Mapped[User | None] = relationship(
        "User", foreign_keys=[user_id], back_populates="settings", lazy="raise"
    )
    project: Mapped[Project | None] = relationship(
        "Project", back_populates="settings", lazy="raise"
    )
    social_account: Mapped[SocialAccount | None] = relationship(
        "SocialAccount", back_populates="settings", lazy="raise"
    )
    definition: Mapped[SettingDefinition] = relationship(
        "SettingDefinition", back_populates="settings", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Setting(id={self.id!r}, scope_type={self.scope_type!r})"
