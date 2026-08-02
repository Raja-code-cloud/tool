"""Unit tests for repository specification composition."""

from __future__ import annotations

import pytest
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import SpecificationError
from cloud_content_hub.infrastructure.repositories.sqlalchemy.specification import (
    AndSpecification,
    AttributeEquals,
    CustomSpecification,
    NotSpecification,
    OrSpecification,
)


class SampleBase(DeclarativeBase):
    pass


class SampleModel(SampleBase):
    __tablename__ = "sample_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String, nullable=False)


def test_attribute_equals_builds_expression() -> None:
    specification = AttributeEquals("status", "active")
    expression = specification.to_expression(SampleModel)
    statement = select(SampleModel).where(expression)
    assert "status" in str(statement)


def test_and_or_not_specifications_compose() -> None:
    active = AttributeEquals("status", "active")
    archived = AttributeEquals("status", "archived")
    combined = (active & archived) | (~active)
    expression = combined.to_expression(SampleModel)
    statement = select(SampleModel).where(expression)
    assert "status" in str(statement)
    assert isinstance(combined, OrSpecification)
    assert isinstance(active & archived, AndSpecification)
    assert isinstance(~active, NotSpecification)


def test_custom_specification_requires_callable_factory() -> None:
    specification = CustomSpecification("not-callable")
    with pytest.raises(SpecificationError, match="callable"):
        specification.to_expression(SampleModel)


def test_unknown_attribute_raises_specification_error() -> None:
    specification = AttributeEquals("missing", "value")
    with pytest.raises(SpecificationError, match="missing"):
        specification.to_expression(SampleModel)
