"""Versioned workspace AI prompt template model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
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
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class AIPromptTemplate(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable, versioned workspace prompt policy."""

    __tablename__ = "ai_prompt_templates"
    __table_args__ = (
        CheckConstraint("template_version > 0", name="ck_ai_prompt_templates__template_version"),
        UniqueConstraint("workspace_id", "id", name="uq_ai_prompt_templates__workspace_id_id"),
        Index(
            "ix_ai_prompt_templates__workspace_name_version_desc",
            "workspace_id",
            "name",
            text("template_version DESC"),
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Versioned workspace prompt policy templates."},
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    template_text: Mapped[str] = mapped_column(Text, nullable=False)
    template_version: Mapped[int] = mapped_column(Integer, nullable=False)
    input_schema: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="ai_prompt_templates", lazy="raise"
    )
    generation_requests: Mapped[list[AIGenerationRequest]] = relationship(
        "AIGenerationRequest",
        back_populates="prompt_template",
        lazy="raise",
        overlaps="asset,source_version,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return (
            f"AIPromptTemplate(id={self.id!r}, name={self.name!r}, "
            f"template_version={self.template_version!r})"
        )
