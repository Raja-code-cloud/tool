"""Sorting helpers with safe column validation."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from sqlalchemy import Select
from sqlalchemy.orm import InstrumentedAttribute

from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import SpecificationError


class SortDirection(StrEnum):
    """Supported sort directions."""

    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True, slots=True)
class SortColumn:
    """One validated sort column and direction."""

    name: str
    direction: SortDirection = SortDirection.ASC


def validate_sort_columns(
    sort_columns: Sequence[SortColumn],
    allowed_columns: frozenset[str],
) -> None:
    """Ensure every requested sort column is explicitly allowed."""

    unknown = {column.name for column in sort_columns if column.name not in allowed_columns}
    if unknown:
        joined = ", ".join(sorted(unknown))
        raise SpecificationError(f"Unsupported sort columns: {joined}")


def apply_sorting(
    statement: Select[Any],
    model: type[Any],
    sort_columns: Sequence[SortColumn],
    allowed_columns: frozenset[str],
) -> Select[Any]:
    """Apply validated ordering clauses to a select statement."""

    if not sort_columns:
        return statement

    validate_sort_columns(sort_columns, allowed_columns)
    orderings: list[Any] = []
    for sort_column in sort_columns:
        attribute = getattr(model, sort_column.name)
        if not isinstance(attribute, InstrumentedAttribute):
            raise SpecificationError(f"Sort column {sort_column.name!r} is not a mapped attribute.")
        orderings.append(
            attribute.desc() if sort_column.direction is SortDirection.DESC else attribute.asc()
        )
    return statement.order_by(*orderings)


def parse_sort_columns(raw: Iterable[str]) -> tuple[SortColumn, ...]:
    """Parse API-style sort tokens such as ``-updated_at`` or ``name``."""

    parsed: list[SortColumn] = []
    for token in raw:
        if token.startswith("-"):
            parsed.append(SortColumn(name=token[1:], direction=SortDirection.DESC))
        elif token.startswith("+"):
            parsed.append(SortColumn(name=token[1:], direction=SortDirection.ASC))
        else:
            parsed.append(SortColumn(name=token, direction=SortDirection.ASC))
    return tuple(parsed)
