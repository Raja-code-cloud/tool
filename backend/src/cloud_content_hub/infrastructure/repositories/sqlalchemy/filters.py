"""Filtering helpers for repository queries."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy import ColumnElement, Select, and_, or_
from sqlalchemy.orm import InstrumentedAttribute

from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import SpecificationError


@dataclass(frozen=True, slots=True)
class RepositoryFilter:
    """Common repository filter parameters."""

    search: str | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    updated_after: datetime | None = None
    updated_before: datetime | None = None
    status: str | None = None
    platform: str | None = None
    tags: frozenset[str] = field(default_factory=frozenset)
    custom: Mapping[str, object] = field(default_factory=dict)


def apply_filters(
    statement: Select[Any],
    model: type[Any],
    filters: RepositoryFilter | None,
    *,
    search_columns: Sequence[str] = (),
    filterable_columns: Mapping[str, str] | None = None,
) -> Select[Any]:
    """Apply standard and custom filters to a select statement."""

    if filters is None:
        return statement

    expressions = list(
        _build_filter_expressions(model, filters, search_columns, filterable_columns)
    )
    if filters.tags:
        tag_column = getattr(model, "tags", None)
        if isinstance(tag_column, InstrumentedAttribute):
            expressions.append(tag_column.contains(list(filters.tags)))
        else:
            raise SpecificationError(
                "Tag filtering requires a mapped tags attribute or a custom specification."
            )

    if not expressions:
        return statement
    return statement.where(and_(*expressions))


def _build_filter_expressions(
    model: type[Any],
    filters: RepositoryFilter,
    search_columns: Sequence[str],
    filterable_columns: Mapping[str, str] | None,
) -> list[ColumnElement[bool]]:
    expressions: list[ColumnElement[bool]] = []

    if filters.search and search_columns:
        search_term = f"%{filters.search.strip()}%"
        search_parts = []
        for column_name in search_columns:
            column = _require_column(model, column_name)
            search_parts.append(column.ilike(search_term))
        expressions.append(or_(*search_parts))

    timestamp_filters = (
        ("created_at", filters.created_after, filters.created_before),
        ("updated_at", filters.updated_after, filters.updated_before),
    )
    for column_name, lower_bound, upper_bound in timestamp_filters:
        raw_column = getattr(model, column_name, None)
        if not isinstance(raw_column, InstrumentedAttribute):
            continue
        column = raw_column
        if lower_bound is not None:
            expressions.append(column >= lower_bound)
        if upper_bound is not None:
            expressions.append(column <= upper_bound)

    if filters.status is not None:
        expressions.append(_require_column(model, "status") == filters.status)

    if filters.platform is not None:
        platform_column = _resolve_filterable_column(model, filterable_columns, "platform")
        expressions.append(platform_column == filters.platform)

    for key, value in filters.custom.items():
        column_name = _resolve_filterable_columns_name(filterable_columns, key)
        expressions.append(_require_column(model, column_name) == value)

    return expressions


def _resolve_filterable_columns_name(
    filterable_columns: Mapping[str, str] | None,
    key: str,
) -> str:
    if filterable_columns is not None and key in filterable_columns:
        return filterable_columns[key]
    return key


def _resolve_filterable_column(
    model: type[Any],
    filterable_columns: Mapping[str, str] | None,
    key: str,
) -> InstrumentedAttribute[Any]:
    column_name = _resolve_filterable_columns_name(filterable_columns, key)
    return _require_column(model, column_name)


def _require_column(model: type[Any], column_name: str) -> InstrumentedAttribute[Any]:
    column = getattr(model, column_name, None)
    if not isinstance(column, InstrumentedAttribute):
        raise SpecificationError(
            f"Model {model.__name__!r} has no filterable attribute {column_name!r}."
        )
    return column
