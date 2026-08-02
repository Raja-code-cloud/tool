"""Brand voice and default settings model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class BrandProfile(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable brand voice, audience, and default style settings."""

    __tablename__ = "brand_profiles"
    __table_args__ = (
        UniqueConstraint("workspace_id", "id", name="uq_brand_profiles__workspace_id_id"),
        Index(
            "uq_brand_profiles__workspace_name_where_active",
            "workspace_id",
            "name",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_brand_profiles__one_default",
            "workspace_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND is_default"),
        ),
        {"comment": "Brand voice guidelines and workspace default settings."},
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    voice_guidelines: Mapped[str | None] = mapped_column(Text, nullable=True)
    audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_language: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'en'"))
    style_settings: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="brand_profiles", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"BrandProfile(id={self.id!r}, name={self.name!r})"
