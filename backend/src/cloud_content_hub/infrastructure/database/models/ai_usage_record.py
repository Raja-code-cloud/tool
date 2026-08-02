"""Immutable AI provider usage and cost evidence model."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.ai_generation_request import (
        AIGenerationRequest,
    )
    from cloud_content_hub.infrastructure.database.models.ai_model import AIModel
    from cloud_content_hub.infrastructure.database.models.ai_provider import AIProvider
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class AIUsageRecord(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Append-only normalized provider usage and cost evidence."""

    __tablename__ = "ai_usage_records"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "generation_request_id"],
            ["ai_generation_requests.workspace_id", "ai_generation_requests.id"],
            name="fk_ai_usage_records__generation_request",
            ondelete="RESTRICT",
        ),
        CheckConstraint("input_tokens >= 0", name="ck_ai_usage_records__input_tokens"),
        CheckConstraint("output_tokens >= 0", name="ck_ai_usage_records__output_tokens"),
        CheckConstraint("total_tokens >= 0", name="ck_ai_usage_records__total_tokens"),
        CheckConstraint(
            "provider_units IS NULL OR provider_units >= 0",
            name="ck_ai_usage_records__provider_units",
        ),
        CheckConstraint("cost_amount >= 0", name="ck_ai_usage_records__cost_amount"),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_ai_usage_records__immutable_uac",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_ai_usage_records__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "generation_request_id",
            "provider_id",
            "model_id",
            name="uq_ai_usage_records__request_provider_model",
        ),
        Index(
            "ix_ai_usage_records__workspace_created",
            "workspace_id",
            text("created_at DESC"),
            text("id DESC"),
        ),
        Index(
            "ix_ai_usage_records__provider_created",
            "provider_id",
            text("created_at DESC"),
            text("id DESC"),
        ),
        Index(
            "ix_ai_usage_records__model_created",
            "model_id",
            text("created_at DESC"),
            text("id DESC"),
        ),
        Index("ix_ai_usage_records__created_at", "created_at", "id"),
        {"comment": "Immutable normalized AI provider usage and cost evidence."},
    )

    generation_request_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=False
    )
    provider_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("ai_providers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    model_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("ai_models.id", ondelete="RESTRICT"),
        nullable=False,
    )
    input_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default=text("0"))
    output_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default=text("0"))
    total_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default=text("0"))
    provider_units: Mapped[Decimal | None] = mapped_column(Numeric(20, 6), nullable=True)
    cost_amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    provider_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="ai_usage_records",
        lazy="raise",
        overlaps="usage_records",
    )
    generation_request: Mapped[AIGenerationRequest] = relationship(
        "AIGenerationRequest",
        back_populates="usage_records",
        lazy="raise",
        overlaps="workspace",
    )
    provider: Mapped[AIProvider] = relationship(
        "AIProvider", back_populates="usage_records", lazy="raise"
    )
    model: Mapped[AIModel] = relationship("AIModel", back_populates="usage_records", lazy="raise")

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return (
            f"AIUsageRecord(id={self.id!r}, generation_request_id={self.generation_request_id!r})"
        )
