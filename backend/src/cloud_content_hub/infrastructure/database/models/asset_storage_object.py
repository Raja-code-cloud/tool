"""Asset and storage object attachment junction model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import StorageObjectPurpose
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.storage_object import StorageObject
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class AssetStorageObject(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Junction row attaching storage blobs or renditions to content assets."""

    __tablename__ = "asset_storage_objects"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_asset_storage_objects__asset",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "storage_object_id"],
            ["storage_objects.workspace_id", "storage_objects.id"],
            name="fk_asset_storage_objects__storage_object",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            check_in(StorageObjectPurpose, name="purpose"),
            name="ck_asset_storage_objects__purpose",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_asset_storage_objects__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "asset_id",
            "purpose",
            "variant_key",
            "position",
            name="uq_asset_storage_objects__asset_purpose_variant_position",
        ),
        Index(
            "ix_asset_storage_objects__workspace_asset_purpose",
            "workspace_id",
            "asset_id",
            "purpose",
            "variant_key",
            "position",
        ),
        Index(
            "ix_asset_storage_objects__workspace_object",
            "workspace_id",
            "storage_object_id",
        ),
        {"comment": "Named blob attachments and renditions for content assets."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    storage_object_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    variant_key: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'original'")
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="asset_storage_objects", lazy="raise"
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="asset_storage_objects",
        lazy="raise",
        overlaps="workspace",
    )
    storage_object: Mapped[StorageObject] = relationship(
        "StorageObject",
        back_populates="asset_links",
        lazy="raise",
        overlaps="asset,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"AssetStorageObject(id={self.id!r}, purpose={self.purpose!r})"
