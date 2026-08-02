"""Typed content asset relation junction model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import ContentRelationType
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class ContentRelation(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Junction row representing a typed directed link between content assets."""

    __tablename__ = "content_relations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "source_asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_content_relations__source_asset",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "target_asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_content_relations__target_asset",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            check_in(ContentRelationType, name="relation_type"),
            name="ck_content_relations__relation_type",
        ),
        CheckConstraint(
            "source_asset_id <> target_asset_id",
            name="ck_content_relations__distinct_assets",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_content_relations__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "source_asset_id",
            "target_asset_id",
            "relation_type",
            name="uq_content_relations__source_target_type",
        ),
        Index(
            "ix_content_relations__workspace_source",
            "workspace_id",
            "source_asset_id",
        ),
        Index(
            "ix_content_relations__workspace_target",
            "workspace_id",
            "target_asset_id",
        ),
        {"comment": "Typed directed links among content assets."},
    )

    source_asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    target_asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    relation_type: Mapped[str] = mapped_column(Text, nullable=False)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="content_relations", lazy="raise"
    )
    source_asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        foreign_keys=[source_asset_id],
        back_populates="outgoing_relations",
        lazy="raise",
    )
    target_asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        foreign_keys=[target_asset_id],
        back_populates="incoming_relations",
        lazy="raise",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"ContentRelation(id={self.id!r}, relation_type={self.relation_type!r})"
