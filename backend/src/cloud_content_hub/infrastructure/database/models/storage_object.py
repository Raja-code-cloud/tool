"""Private blob storage metadata model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Index,
    LargeBinary,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import ScanStatus
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.asset_storage_object import (
        AssetStorageObject,
    )
    from cloud_content_hub.infrastructure.database.models.data_export import DataExport
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class StorageObject(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable private blob metadata for tenant-scoped object storage."""

    __tablename__ = "storage_objects"
    __table_args__ = (
        CheckConstraint("byte_size >= 0", name="ck_storage_objects__byte_size"),
        CheckConstraint(
            check_in(ScanStatus, name="scan_status"),
            name="ck_storage_objects__scan_status",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_storage_objects__workspace_id_id"),
        Index(
            "uq_storage_objects__workspace_object_key_where_active",
            "workspace_id",
            "object_key",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_storage_objects__workspace_scan_due",
            "workspace_id",
            "created_at",
            "id",
            postgresql_where=text("deleted_at IS NULL AND scan_status IN ('pending','failed')"),
        ),
        Index(
            "ix_storage_objects__workspace_checksum",
            "workspace_id",
            "checksum_sha256",
            "byte_size",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Private blob metadata; URLs are never stored directly."},
    )

    object_key: Mapped[str] = mapped_column(Text, nullable=False)
    storage_provider: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'azure_blob'")
    )
    container_name: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(Text, nullable=False)
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    scan_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text(f"'{ScanStatus.PENDING.value}'"),
    )
    scan_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    encryption_key_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    retention_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="storage_objects", lazy="raise"
    )
    asset_links: Mapped[list[AssetStorageObject]] = relationship(
        "AssetStorageObject",
        back_populates="storage_object",
        lazy="raise",
        overlaps="asset,asset_storage_objects,workspace",
    )

    data_exports: Mapped[list[DataExport]] = relationship(
        "DataExport", back_populates="storage_object", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"StorageObject(id={self.id!r}, object_key={self.object_key!r})"
