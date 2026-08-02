"""AI provider catalog ORM model."""

from typing import Any

from sqlalchemy import CheckConstraint, Index, Text, text
from sqlalchemy.dialects.postgresql import CITEXT, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin


class AIProvider(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Extensible global AI provider catalog entry."""

    __tablename__ = "ai_providers"
    __table_args__ = (
        CheckConstraint(
            "status IN ('enabled', 'disabled', 'degraded')",
            name="status_values",
        ),
        Index("uq_ai_providers__code", "code", unique=True),
        {"comment": "Extensible global AI provider catalog."},
    )

    code: Mapped[str] = mapped_column(CITEXT(), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'enabled'"))
    capabilities: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    secret_config_ref: Mapped[str | None] = mapped_column(Text)

    models: Mapped[list[Any]] = relationship("AIModel", back_populates="provider", lazy="selectin")
    usage_records: Mapped[list[Any]] = relationship(
        "AIUsageRecord", back_populates="provider", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"AIProvider(id={self.id!r}, code={self.code!r}, status={self.status!r})"
