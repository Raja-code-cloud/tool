"""Lightweight composable specification pattern for repository queries."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import cast

from sqlalchemy import ColumnElement, and_, not_, or_

from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import SpecificationError


class Specification[ModelT](ABC):
    """Composable filter expression for repository queries."""

    @abstractmethod
    def to_expression(self, model: type[ModelT]) -> ColumnElement[bool]:
        """Translate the specification into a SQLAlchemy boolean expression."""

    def __and__(self, other: Specification[ModelT]) -> Specification[ModelT]:
        return AndSpecification(self, other)

    def __or__(self, other: Specification[ModelT]) -> Specification[ModelT]:
        return OrSpecification(self, other)

    def __invert__(self) -> Specification[ModelT]:
        return NotSpecification(self)


class AndSpecification[ModelT](Specification[ModelT]):
    """Logical AND of two specifications."""

    def __init__(self, left: Specification[ModelT], right: Specification[ModelT]) -> None:
        self._left = left
        self._right = right

    def to_expression(self, model: type[ModelT]) -> ColumnElement[bool]:
        return and_(self._left.to_expression(model), self._right.to_expression(model))


class OrSpecification[ModelT](Specification[ModelT]):
    """Logical OR of two specifications."""

    def __init__(self, left: Specification[ModelT], right: Specification[ModelT]) -> None:
        self._left = left
        self._right = right

    def to_expression(self, model: type[ModelT]) -> ColumnElement[bool]:
        return or_(self._left.to_expression(model), self._right.to_expression(model))


class NotSpecification[ModelT](Specification[ModelT]):
    """Logical NOT of a specification."""

    def __init__(self, inner: Specification[ModelT]) -> None:
        self._inner = inner

    def to_expression(self, model: type[ModelT]) -> ColumnElement[bool]:
        return not_(self._inner.to_expression(model))


class AttributeEquals[ModelT](Specification[ModelT]):
    """Match a model attribute against a constant value."""

    def __init__(self, attribute: str, value: object) -> None:
        self._attribute = attribute
        self._value = value

    def to_expression(self, model: type[ModelT]) -> ColumnElement[bool]:
        column = getattr(model, self._attribute, None)
        if column is None:
            raise SpecificationError(
                f"Model {model.__name__!r} has no attribute {self._attribute!r}."
            )
        return cast(ColumnElement[bool], column == self._value)


class CustomSpecification[ModelT](Specification[ModelT]):
    """Wrap an arbitrary expression factory for one-off repository filters."""

    def __init__(
        self,
        expression_factory: object,
    ) -> None:
        self._expression_factory = expression_factory

    def to_expression(self, model: type[ModelT]) -> ColumnElement[bool]:
        if not callable(self._expression_factory):
            raise SpecificationError("Custom specification factory must be callable.")
        expression = self._expression_factory(model)
        if not isinstance(expression, ColumnElement):
            raise SpecificationError("Custom specification must return a SQLAlchemy expression.")
        return expression
