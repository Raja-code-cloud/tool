"""Unit tests for repository sorting helpers."""


import pytest
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import SpecificationError
from cloud_content_hub.infrastructure.repositories.sqlalchemy.sorting import (
    SortColumn,
    SortDirection,
    apply_sorting,
    parse_sort_columns,
)


class SortBase(DeclarativeBase):
    pass


class SortModel(SortBase):
    __tablename__ = "sort_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[str] = mapped_column(String, nullable=False)


def test_parse_sort_columns_supports_signed_tokens() -> None:
    columns = parse_sort_columns(["-updated_at", "+name", "id"])
    assert columns[0] == SortColumn(name="updated_at", direction=SortDirection.DESC)
    assert columns[1].direction is SortDirection.ASC
    assert columns[2].name == "id"


def test_apply_sorting_rejects_unknown_columns() -> None:
    statement = select(SortModel)
    with pytest.raises(SpecificationError, match="Unsupported sort columns"):
        apply_sorting(
            statement,
            SortModel,
            [SortColumn(name="missing")],
            frozenset({"name"}),
        )


def test_apply_sorting_applies_multiple_columns() -> None:
    statement = apply_sorting(
        select(SortModel),
        SortModel,
        [
            SortColumn(name="updated_at", direction=SortDirection.DESC),
            SortColumn(name="name", direction=SortDirection.ASC),
        ],
        frozenset({"updated_at", "name"}),
    )
    compiled = str(statement)
    assert "updated_at" in compiled
    assert "name" in compiled
