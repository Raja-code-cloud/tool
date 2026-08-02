"""Immutable organization and workspace usage event model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import IMMUTABLE_UAC_CHECK
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.organization import Organization
    from cloud_content_hub.infrastructure.database.models.usage_dimension import UsageDimension
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class UsageEvent(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Append-only, deduplicated metering fact."""

    __tablename__ = "usage_events"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_usage_events__quantity"),
        CheckConstraint("cost_amount IS NULL OR cost_amount >= 0", name="ck_usage_events__cost"),
        CheckConstraint(IMMUTABLE_UAC_CHECK, name="ck_usage_events__immutable_uac"),
        UniqueConstraint("workspace_id", "id", name="uq_usage_events__workspace_id_id"),
        UniqueConstraint("workspace_id", "dedupe_key", name="uq_usage_events__workspace_dedupe"),
        Index(
            "ix_usage_events__workspace_dimension_time",
            "workspace_id",
            "usage_dimension_id",
            text("occurred_at DESC"),
            text("id DESC"),
        ),
        Index(
            "ix_usage_events__organization_dimension_time",
            "organization_id",
            "usage_dimension_id",
            text("occurred_at DESC"),
            text("id DESC"),
        ),
        Index(
            "brin_usage_events__occurred_at",
            "occurred_at",
            postgresql_using="brin",
            postgresql_with={"pages_per_range": 64},
        ),
        {"comment": "Immutable metering facts retained under usage and billing policy."},
    )

    organization_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    usage_dimension_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("usage_dimensions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_type: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    dedupe_key: Mapped[str] = mapped_column(Text, nullable=False)
    cost_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="usage_events", lazy="raise"
    )
    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="usage_events", lazy="raise"
    )
    usage_dimension: Mapped[UsageDimension] = relationship(
        "UsageDimension", back_populates="events", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"UsageEvent(id={self.id!r}, occurred_at={self.occurred_at!r})"
