"""Curated content collection model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import CollectionVisibility
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.collection_item import CollectionItem
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Collection(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable curated set of content assets."""

    __tablename__ = "collections"
    __table_args__ = (
        CheckConstraint(
            check_in(CollectionVisibility, name="visibility"),
            name="ck_collections__visibility",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_collections__workspace_id_id"),
        Index(
            "uq_collections__workspace_name_where_active",
            "workspace_id",
            "name",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_collections__workspace_updated_cursor",
            "workspace_id",
            text("updated_at DESC"),
            "id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Curated ordered content sets within a workspace."},
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    visibility: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text(f"'{CollectionVisibility.WORKSPACE.value}'"),
    )
    owner_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="collections", lazy="raise"
    )
    items: Mapped[list[CollectionItem]] = relationship(
        "CollectionItem", back_populates="collection", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Collection(id={self.id!r}, name={self.name!r})"
