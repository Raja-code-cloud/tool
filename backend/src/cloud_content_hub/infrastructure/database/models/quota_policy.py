"""Organization or workspace quota policy model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, Text, text
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


class QuotaPolicy(UUIDPrimaryKeyMixin, OrganizationMixin, UACMixin, Base):
    """Effective-dated metered-resource limit at organization or workspace scope."""

    __tablename__ = "quota_policies"
    __table_args__ = (
        CheckConstraint(
            "period_kind IN ('day','month','billing_cycle','lifetime')",
            name="ck_quota_policies__period_kind",
        ),
        CheckConstraint("hard_limit >= 0", name="ck_quota_policies__hard_limit"),
        CheckConstraint(
            "soft_limit IS NULL OR (soft_limit >= 0 AND soft_limit <= hard_limit)",
            name="ck_quota_policies__soft_limit",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_quota_policies__effective_range",
        ),
        Index(
            "uq_quota_policies__scope_dimension_effective",
            "organization_id",
            "workspace_id",
            "usage_dimension_id",
            "effective_from",
            unique=True,
            postgresql_nulls_not_distinct=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_quota_policies__workspace_dimension_effective",
            "workspace_id",
            "usage_dimension_id",
            text("effective_from DESC"),
            postgresql_where=text("deleted_at IS NULL AND workspace_id IS NOT NULL"),
        ),
        Index(
            "ix_quota_policies__organization_dimension_effective",
            "organization_id",
            "usage_dimension_id",
            text("effective_from DESC"),
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Effective-dated organization or workspace quota limits."},
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
    period_kind: Mapped[str] = mapped_column(Text, nullable=False)
    hard_limit: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    soft_limit: Mapped[Decimal | None] = mapped_column(Numeric(30, 10), nullable=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="quota_policies", lazy="raise"
    )
    workspace: Mapped[Workspace | None] = relationship(
        "Workspace", back_populates="quota_policies", lazy="raise"
    )
    usage_dimension: Mapped[UsageDimension] = relationship(
        "UsageDimension", back_populates="quota_policies", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"QuotaPolicy(id={self.id!r}, period_kind={self.period_kind!r})"
