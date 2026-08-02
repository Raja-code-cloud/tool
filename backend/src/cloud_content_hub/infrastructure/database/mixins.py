"""Composable columns shared by database models."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class UUIDPrimaryKeyMixin:
    """Provide an application-generated PostgreSQL UUID ``id`` primary key."""

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


class TimestampMixin:
    """Provide UTC creation and last-update instants."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )


class AuditActorMixin:
    """Record nullable user principals responsible for row changes."""

    created_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )


class SoftDeleteMixin:
    """Provide the universal nullable soft-deletion instant."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class VersionMixin:
    """Provide SQLAlchemy optimistic-concurrency versioning."""

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    @declared_attr.directive
    def __mapper_args__(cls) -> dict[str, object]:
        """Configure compare-and-increment behavior for mutable rows."""

        return {"version_id_col": cls.version}


class UniversalAuditMixin(
    TimestampMixin,
    AuditActorMixin,
    SoftDeleteMixin,
    VersionMixin,
):
    """Provide all universal audit columns required on every table."""


class WorkspaceScopedMixin:
    """Provide the required operational tenant key."""

    workspace_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )


class OptionalWorkspaceScopedMixin:
    """Provide an optional workspace key for mixed global/workspace tables."""

    workspace_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )


class OrganizationScopedMixin:
    """Provide the required commercial organization key."""

    organization_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )


class OptionalOrganizationScopedMixin:
    """Provide an optional organization key for mixed-scope tables."""

    organization_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )


# Concise public aliases for model declarations.
UACMixin = UniversalAuditMixin
AuditMixin = AuditActorMixin
WorkspaceMixin = WorkspaceScopedMixin
OrganizationMixin = OrganizationScopedMixin
