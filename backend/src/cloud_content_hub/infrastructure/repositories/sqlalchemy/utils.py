"""Shared query helpers for SQLAlchemy repositories."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID

from sqlalchemy import ColumnElement, Select, func, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import DuplicateEntity
from cloud_content_hub.infrastructure.repositories.sqlalchemy.filters import (
    RepositoryFilter,
    apply_filters,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.sorting import (
    SortColumn,
    apply_sorting,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.specification import Specification


def utc_now() -> datetime:
    """Return the current UTC instant for repository mutations."""

    return datetime.now(tz=UTC)


def has_attribute(model: type[Any], attribute_name: str) -> bool:
    """Return whether a mapped attribute exists on the model."""

    return isinstance(getattr(model, attribute_name, None), InstrumentedAttribute)


def active_row_expression(model: type[Any]) -> ColumnElement[bool] | None:
    """Return the active-row predicate when the model supports soft delete."""

    deleted_at = getattr(model, "deleted_at", None)
    if isinstance(deleted_at, InstrumentedAttribute):
        return deleted_at.is_(None)
    return None


def apply_active_scope(
    statement: Select[Any],
    model: type[Any],
    *,
    include_deleted: bool,
) -> Select[Any]:
    """Apply the active-row predicate unless deleted rows are requested."""

    if include_deleted:
        return statement
    expression = active_row_expression(model)
    if expression is None:
        return statement
    return statement.where(expression)


def apply_specification(
    statement: Select[Any],
    model: type[Any],
    specification: Specification[Any] | None,
) -> Select[Any]:
    """Apply a composable specification to a select statement."""

    if specification is None:
        return statement
    return statement.where(specification.to_expression(model))


def apply_workspace_scope(
    statement: Select[Any],
    model: type[Any],
    workspace_id: UUID,
) -> Select[Any]:
    """Apply an explicit workspace predicate for tenant-safe reads."""

    workspace_column = getattr(model, "workspace_id", None)
    if not isinstance(workspace_column, InstrumentedAttribute):
        raise ValueError(f"Model {model.__name__!r} is not workspace-scoped.")
    return statement.where(workspace_column == workspace_id)


def build_select(
    model: type[Any],
    *,
    include_deleted: bool = False,
    specification: Specification[Any] | None = None,
    filters: RepositoryFilter | None = None,
    sort: tuple[SortColumn, ...] | None = None,
    allowed_sort_columns: frozenset[str] | None = None,
    search_columns: tuple[str, ...] = (),
    filterable_columns: dict[str, str] | None = None,
    workspace_id: UUID | None = None,
) -> Select[Any]:
    """Build a reusable select statement with common repository scopes."""

    statement = select(model)
    if workspace_id is not None:
        statement = apply_workspace_scope(statement, model, workspace_id)
    statement = apply_active_scope(statement, model, include_deleted=include_deleted)
    statement = apply_specification(statement, model, specification)
    statement = apply_filters(
        statement,
        model,
        filters,
        search_columns=search_columns,
        filterable_columns=filterable_columns,
    )
    if sort and allowed_sort_columns is not None:
        statement = apply_sorting(statement, model, sort, allowed_sort_columns)
    return statement


async def execute_count(session: AsyncSession, statement: Select[Any]) -> int:
    """Execute a count query derived from a select statement."""

    count_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    result = await session.scalar(count_statement)
    return int(result or 0)


def translate_integrity_error(error: IntegrityError, *, entity_name: str) -> DuplicateEntity:
    """Translate a database integrity failure into a repository duplicate error."""

    return DuplicateEntity(f"{entity_name} violates a uniqueness constraint.")


async def soft_delete_by_id(
    session: AsyncSession,
    model: type[Any],
    entity_id: UUID,
    *,
    expected_version: int,
    updated_by: UUID | None = None,
    workspace_id: UUID | None = None,
) -> int:
    """Soft-delete one row with optimistic concurrency."""

    values: dict[str, object] = {
        "deleted_at": utc_now(),
        "updated_at": utc_now(),
        "version": expected_version + 1,
    }
    if updated_by is not None and has_attribute(model, "updated_by"):
        values["updated_by"] = updated_by

    where_clauses = [
        model.id == entity_id,
        model.version == expected_version,
    ]
    active_expression = active_row_expression(model)
    if active_expression is not None:
        where_clauses.append(active_expression)
    if workspace_id is not None:
        where_clauses.append(model.workspace_id == workspace_id)

    statement = update(model).where(*where_clauses).values(**values)
    result = await session.execute(statement)
    return int(cast(CursorResult[Any], result).rowcount or 0)


async def restore_by_id(
    session: AsyncSession,
    model: type[Any],
    entity_id: UUID,
    *,
    expected_version: int,
    updated_by: UUID | None = None,
    workspace_id: UUID | None = None,
) -> int:
    """Restore one soft-deleted row with optimistic concurrency."""

    values: dict[str, object] = {
        "deleted_at": None,
        "updated_at": utc_now(),
        "version": expected_version + 1,
    }
    if updated_by is not None and has_attribute(model, "updated_by"):
        values["updated_by"] = updated_by

    where_clauses = [
        model.id == entity_id,
        model.version == expected_version,
        model.deleted_at.is_not(None),
    ]
    if workspace_id is not None:
        where_clauses.append(model.workspace_id == workspace_id)

    statement = update(model).where(*where_clauses).values(**values)
    result = await session.execute(statement)
    return int(cast(CursorResult[Any], result).rowcount or 0)
