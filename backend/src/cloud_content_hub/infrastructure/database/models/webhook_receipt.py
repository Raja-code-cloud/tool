"""Inbound provider webhook receipt model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class WebhookReceipt(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Immutable, redacted receipt used to deduplicate provider callbacks."""

    __tablename__ = "webhook_receipts"
    __table_args__ = (
        CheckConstraint(
            "processing_status IN ('received','processed','ignored','failed')",
            name="webhook_receipts_processing_status",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="webhook_receipts_immutable_shape",
        ),
        Index(
            "uq_webhook_receipts__provider_external",
            "provider_code",
            "external_event_id",
            unique=True,
        ),
        Index(
            "uq_webhook_receipts__provider_payload_hash",
            "provider_code",
            "payload_hash",
            unique=True,
            postgresql_where=text("external_event_id = ''"),
        ),
        Index(
            "ix_webhook_receipts__unprocessed",
            "received_at",
            "id",
            postgresql_where=text(
                "processed_at IS NULL AND processing_status IN ('received','failed')"
            ),
        ),
        {"comment": "Immutable redacted inbound callback deduplication evidence."},
    )

    workspace_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=True,
    )
    provider_code: Mapped[str] = mapped_column(Text, nullable=False)
    external_event_id: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    signature_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    payload_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    payload_fragment: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_status: Mapped[str] = mapped_column(Text, nullable=False)

    workspace: Mapped[Workspace | None] = relationship(
        "Workspace", back_populates="webhook_receipts", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe representation without callback identifiers."""

        return f"WebhookReceipt(id={self.id!r}, provider_code={self.provider_code!r})"
