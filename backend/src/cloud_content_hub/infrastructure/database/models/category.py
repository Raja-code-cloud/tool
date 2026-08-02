"""Controlled hierarchical taxonomy category model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.asset_category import AssetCategory
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Category(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable hierarchical controlled taxonomy category."""

    __tablename__ = "categories"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "parent_category_id"],
            ["categories.workspace_id", "categories.id"],
            name="fk_categories__parent",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "parent_category_id IS NULL OR parent_category_id <> id",
            name="ck_categories__parent_not_self",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_categories__workspace_id_id"),
        Index(
            "uq_categories__workspace_slug_where_active",
            "workspace_id",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_categories__workspace_parent",
            "workspace_id",
            "parent_category_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Controlled hierarchical taxonomy within a workspace."},
    )

    parent_category_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(CITEXT, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="categories", lazy="raise"
    )
    parent_category: Mapped[Category | None] = relationship(
        "Category",
        remote_side="Category.id",
        foreign_keys=[parent_category_id],
        back_populates="child_categories",
        lazy="raise",
    )
    child_categories: Mapped[list[Category]] = relationship(
        "Category",
        back_populates="parent_category",
        lazy="raise",
        overlaps="workspace",
    )
    asset_categories: Mapped[list[AssetCategory]] = relationship(
        "AssetCategory",
        back_populates="category",
        lazy="raise",
        overlaps="asset,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Category(id={self.id!r}, slug={self.slug!r})"
