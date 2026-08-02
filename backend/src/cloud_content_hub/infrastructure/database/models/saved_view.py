"""Persisted library and analytics filter view model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import SavedViewType
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class SavedView(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable persisted filter and sort view for library or analytics."""

    __tablename__ = "saved_views"
    __table_args__ = (
        CheckConstraint(
            check_in(SavedViewType, name="view_type"),
            name="ck_saved_views__view_type",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_saved_views__workspace_id_id"),
        Index(
            "uq_saved_views__workspace_owner_type_name_where_active",
            "workspace_id",
            "owner_id",
            "view_type",
            "name",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_saved_views__workspace_owner_type",
            "workspace_id",
            "owner_id",
            "view_type",
            "name",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Persisted library, calendar, analytics, and activity filters."},
    )

    owner_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    view_type: Mapped[str] = mapped_column(Text, nullable=False)
    filter_spec: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    sort_spec: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    is_shared: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="saved_views", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"SavedView(id={self.id!r}, name={self.name!r})"
