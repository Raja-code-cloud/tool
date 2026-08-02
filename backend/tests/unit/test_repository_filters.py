"""Unit tests for repository filter helpers."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import DateTime, Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import SpecificationError
from cloud_content_hub.infrastructure.repositories.sqlalchemy.filters import (
    RepositoryFilter,
    apply_filters,
)


class FilterBase(DeclarativeBase):
    pass


class FilterModel(FilterBase):
    __tablename__ = "filter_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def test_apply_filters_builds_search_and_timestamp_predicates() -> None:
    filters = RepositoryFilter(
        search="alpha",
        created_after=datetime(2026, 1, 1, tzinfo=UTC),
        updated_before=datetime(2026, 12, 31, tzinfo=UTC),
        status="active",
        platform="linkedin",
    )
    statement = apply_filters(
        select(FilterModel),
        FilterModel,
        filters,
        search_columns=("status", "platform"),
    )
    compiled = str(statement)
    assert "status" in compiled
    assert "platform" in compiled
    assert "created_at" in compiled
    assert "updated_at" in compiled


def test_apply_filters_requires_tag_column_for_tag_filtering() -> None:
    filters = RepositoryFilter(tags=frozenset({"launch"}))
    with pytest.raises(SpecificationError, match="Tag filtering"):
        apply_filters(select(FilterModel), FilterModel, filters)
