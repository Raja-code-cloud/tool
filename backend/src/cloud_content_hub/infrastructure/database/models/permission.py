"""Global stable permission code catalog model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import PermissionRiskLevel
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.role_permission import RolePermission


class Permission(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Global permission-code catalog referenced by role grants."""

    __tablename__ = "permissions"
    __table_args__ = (
        CheckConstraint(
            check_in(PermissionRiskLevel, name="risk_level"),
            name="ck_permissions__risk_level",
        ),
        UniqueConstraint("code", name="uq_permissions__code"),
        {"comment": "Global stable permission codes; retired only when unreferenced."},
    )

    code: Mapped[str] = mapped_column(CITEXT, nullable=False)
    module: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[PermissionRiskLevel] = mapped_column(Text, nullable=False)

    role_permissions: Mapped[list[RolePermission]] = relationship(
        "RolePermission", back_populates="permission", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Permission(id={self.id!r}, code={self.code!r})"
