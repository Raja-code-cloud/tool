"""External billing customer reference model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import BillingCustomerStatus
from cloud_content_hub.infrastructure.database.mixins import (
    OrganizationMixin,
    UACMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.organization import Organization


class BillingCustomer(UUIDPrimaryKeyMixin, OrganizationMixin, UACMixin, Base):
    """Mutable mirror of an external billing provider customer record."""

    __tablename__ = "billing_customers"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active','delinquent','closed')",
            name="ck_billing_customers__status",
        ),
        UniqueConstraint("organization_id", "id", name="uq_billing_customers__organization_id_id"),
        Index(
            "uq_billing_customers__organization_provider_where_active",
            "organization_id",
            "provider_code",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_billing_customers__provider_external",
            "provider_code",
            "external_customer_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "External billing customer reference without payment instruments."},
    )

    provider_code: Mapped[str] = mapped_column(Text, nullable=False)
    external_customer_id: Mapped[str] = mapped_column(Text, nullable=False)
    billing_email: Mapped[str | None] = mapped_column(CITEXT, nullable=True)
    tax_region: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[BillingCustomerStatus] = mapped_column(Text, nullable=False)

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="billing_customers", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"BillingCustomer(id={self.id!r}, status={self.status!r})"
