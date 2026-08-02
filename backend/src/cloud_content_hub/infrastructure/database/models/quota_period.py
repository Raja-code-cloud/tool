"""Concurrency-safe quota period counter model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    OrganizationMixin,
    UACMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.organization import Organization
    from cloud_content_hub.infrastructure.database.models.usage_dimension import UsageDimension
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class QuotaPeriod(UUIDPrimaryKeyMixin, OrganizationMixin, UACMixin, Base):
    """Atomic consumed and reserved quantity counters for a quota interval."""

    __tablename__ = "quota_periods"
    __table_args__ = (
        CheckConstraint("period_end > period_start", name="ck_quota_periods__period"),
        CheckConstraint("consumed_quantity >= 0", name="ck_quota_periods__consumed"),
        CheckConstraint("reserved_quantity >= 0", name="ck_quota_periods__reserved"),
        Index(
            "uq_quota_periods__scope_dimension_period",
            "organization_id",
            "workspace_id",
            "usage_dimension_id",
            "period_start",
            "period_end",
            unique=True,
            postgresql_nulls_not_distinct=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_quota_periods__workspace_dimension_period",
            "workspace_id",
            "usage_dimension_id",
            "period_start",
            "period_end",
            postgresql_where=text("deleted_at IS NULL AND workspace_id IS NOT NULL"),
        ),
        Index(
            "ix_quota_periods__organization_dimension_period",
            "organization_id",
            "usage_dimension_id",
            "period_start",
            "period_end",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Concurrency-safe quota counters and reservations."},
    )

    workspace_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=True,
    )
    usage_dimension_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("usage_dimensions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_quantity: Mapped[Decimal] = mapped_column(
        Numeric(30, 10), nullable=False, server_default=text("0")
    )
    reserved_quantity: Mapped[Decimal] = mapped_column(
        Numeric(30, 10), nullable=False, server_default=text("0")
    )
    last_reconciled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="quota_periods", lazy="raise"
    )
    workspace: Mapped[Workspace | None] = relationship(
        "Workspace", back_populates="quota_periods", lazy="raise"
    )
    usage_dimension: Mapped[UsageDimension] = relationship(
        "UsageDimension", back_populates="quota_periods", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"QuotaPeriod(id={self.id!r}, period_start={self.period_start!r})"
