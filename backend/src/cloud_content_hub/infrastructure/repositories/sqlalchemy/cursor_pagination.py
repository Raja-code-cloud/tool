"""Keyset cursor encoding and SQLAlchemy pagination helpers."""

from __future__ import annotations

import base64
import json
from datetime import datetime
from typing import Any, cast
from uuid import UUID

from sqlalchemy import Select, and_, or_
from sqlalchemy.orm import InstrumentedAttribute

from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import SpecificationError
from cloud_content_hub.infrastructure.repositories.sqlalchemy.sorting import (
    SortColumn,
    SortDirection,
    parse_sort_columns,
)


def encode_keyset_cursor(
    *,
    sort_column: str,
    sort_direction: SortDirection,
    sort_value: str,
    entity_id: UUID,
) -> str:
    """Return an opaque keyset cursor for repository pagination."""

    payload = {
        "s": sort_column,
        "d": sort_direction.value,
        "v": sort_value,
        "i": str(entity_id),
    }
    encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    )
    return encoded.decode().rstrip("=")


def decode_keyset_cursor(cursor: str) -> tuple[str, SortDirection, str, UUID]:
    """Decode an opaque keyset cursor produced by :func:`encode_keyset_cursor`."""

    try:
        raw = base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4))
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("cursor payload must be an object")
        sort_column = payload["s"]
        sort_direction = SortDirection(payload["d"])
        sort_value = payload["v"]
        entity_id = UUID(payload["i"])
        if not isinstance(sort_column, str) or not isinstance(sort_value, str):
            raise ValueError("invalid cursor field types")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SpecificationError("Invalid pagination cursor.") from exc
    return sort_column, sort_direction, sort_value, entity_id


def normalize_sort_token(
    sort: str,
    *,
    allowed_columns: frozenset[str],
    default: str = "-updated_at",
) -> SortColumn:
    """Parse a single sort token and validate it against an allowlist."""

    token = sort.strip() if sort.strip() else default
    columns = parse_sort_columns([token])
    if len(columns) != 1:
        raise SpecificationError("Only one sort column is supported for cursor pagination.")
    column = columns[0]
    if column.name not in allowed_columns:
        raise SpecificationError(f"Unsupported sort column: {column.name}")
    return column


def apply_keyset_pagination[ModelT](
    statement: Select[Any],
    model: type[ModelT],
    *,
    sort_column: SortColumn,
    cursor: str | None,
    limit: int,
) -> Select[Any]:
    """Apply keyset pagination predicates and limit+1 fetch sizing."""

    if limit < 1:
        raise ValueError("limit must be >= 1")

    attribute = getattr(model, sort_column.name)
    if not isinstance(attribute, InstrumentedAttribute):
        raise SpecificationError(f"Sort column {sort_column.name!r} is not mapped.")

    id_column = cast(InstrumentedAttribute[Any], model.id)  # type: ignore[attr-defined]
    if not isinstance(id_column, InstrumentedAttribute):
        raise SpecificationError("Cursor pagination requires a mapped id column.")

    if cursor is not None:
        _, cursor_direction, sort_value, cursor_id = decode_keyset_cursor(cursor)
        if cursor_direction is not sort_column.direction:
            raise SpecificationError("Cursor sort direction does not match the request.")

        if isinstance(attribute.type.python_type, type) and attribute.type.python_type is datetime:
            parsed_value: datetime | str = datetime.fromisoformat(sort_value)
        else:
            parsed_value = sort_value

        if sort_column.direction is SortDirection.DESC:
            statement = statement.where(
                or_(
                    attribute < parsed_value,
                    and_(attribute == parsed_value, id_column < cursor_id),
                )
            )
        else:
            statement = statement.where(
                or_(
                    attribute > parsed_value,
                    and_(attribute == parsed_value, id_column > cursor_id),
                )
            )

    descending = sort_column.direction is SortDirection.DESC
    statement = statement.order_by(
        attribute.desc() if descending else attribute.asc(),
        id_column.desc() if descending else id_column.asc(),
    )
    return statement.limit(limit + 1)


def build_keyset_page[TRecord](
    rows: list[TRecord],
    *,
    limit: int,
    sort_column: SortColumn,
    sort_value_getter: Any,
    id_getter: Any,
) -> tuple[tuple[TRecord, ...], str | None, bool]:
    """Build cursor page metadata from limit+1 fetched rows."""

    has_more = len(rows) > limit
    items = tuple(rows[:limit])
    if not has_more or not items:
        return items, None, has_more

    last = items[-1]
    sort_value = sort_value_getter(last)
    if isinstance(sort_value, datetime):
        encoded_value = sort_value.isoformat()
    else:
        encoded_value = str(sort_value)

    next_cursor = encode_keyset_cursor(
        sort_column=sort_column.name,
        sort_direction=sort_column.direction,
        sort_value=encoded_value,
        entity_id=id_getter(last),
    )
    return items, next_cursor, has_more
