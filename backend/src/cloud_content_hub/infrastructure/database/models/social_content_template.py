"""Platform content rendering template model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    OptionalWorkspaceScopedMixin,
    UACMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.social_platform import SocialPlatform
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class SocialContentTemplate(UUIDPrimaryKeyMixin, OptionalWorkspaceScopedMixin, UACMixin, Base):
    """Mutable platform content rendering template, global or workspace scoped."""

    __tablename__ = "social_content_templates"
    __table_args__ = (
        CheckConstraint(
            "template_version > 0", name="ck_social_content_templates__template_version"
        ),
        Index(
            "uq_social_content_templates__scope_platform_name_version",
            "workspace_id",
            "platform_id",
            "name",
            "template_version",
            unique=True,
            postgresql_nulls_not_distinct=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Platform content rendering templates with global or workspace scope."},
    )

    platform_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("social_platforms.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    template_version: Mapped[int] = mapped_column(Integer, nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    constraints: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    workspace: Mapped[Workspace | None] = relationship(
        "Workspace", back_populates="social_content_templates", lazy="raise"
    )
    platform: Mapped[SocialPlatform] = relationship(
        "SocialPlatform", back_populates="content_templates", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return (
            f"SocialContentTemplate(id={self.id!r}, name={self.name!r}, "
            f"template_version={self.template_version!r})"
        )
