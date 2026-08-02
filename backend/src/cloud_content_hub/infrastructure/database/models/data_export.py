"""Tenant export and erasure package tracking model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import DataExportState, DataExportType
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.storage_object import StorageObject
    from cloud_content_hub.infrastructure.database.models.user import User
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class DataExport(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable workspace export or erasure package lifecycle record."""

    __tablename__ = "data_exports"
    __table_args__ = (
        CheckConstraint(
            "export_type IN ('workspace_export','user_export','erasure_evidence')",
            name="ck_data_exports__export_type",
        ),
        CheckConstraint(
            "state IN ('queued','running','ready','failed','expired','purged')",
            name="ck_data_exports__state",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_data_exports__workspace_id_id"),
        Index(
            "ix_data_exports__workspace_cursor",
            "workspace_id",
            text("updated_at DESC"),
            text("id DESC"),
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_data_exports__expiry",
            "expires_at",
            "id",
            postgresql_where=text("deleted_at IS NULL AND state IN ('ready','expired')"),
        ),
        {"comment": "Tenant export and erasure package tracking with expiry."},
    )

    requested_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    export_type: Mapped[DataExportType] = mapped_column(Text, nullable=False)
    state: Mapped[DataExportState] = mapped_column(Text, nullable=False)
    storage_object_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("storage_objects.id", ondelete="RESTRICT"),
        nullable=True,
    )
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    purged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checksum_sha256: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    failure_code: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="data_exports", lazy="raise"
    )
    requester: Mapped[User | None] = relationship(
        "User", foreign_keys=[requested_by], back_populates="data_exports", lazy="raise"
    )
    storage_object: Mapped[StorageObject | None] = relationship(
        "StorageObject", back_populates="data_exports", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"DataExport(id={self.id!r}, export_type={self.export_type!r}, state={self.state!r})"
