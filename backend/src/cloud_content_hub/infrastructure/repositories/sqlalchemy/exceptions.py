"""Repository-layer exception hierarchy."""

from __future__ import annotations

from typing import ClassVar


class RepositoryException(Exception):
    """Base exception for repository infrastructure failures."""

    default_code: ClassVar[str] = "repository_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(message)


class EntityNotFound(RepositoryException):
    """Raised when a requested entity does not exist or is not visible."""

    default_code = "entity_not_found"


class DuplicateEntity(RepositoryException):
    """Raised when a create or restore violates an active-row uniqueness rule."""

    default_code = "duplicate_entity"


class ConcurrencyConflict(RepositoryException):
    """Raised when optimistic concurrency detects a stale version."""

    default_code = "version_conflict"


class TransactionFailed(RepositoryException):
    """Raised when a unit-of-work transaction cannot be completed."""

    default_code = "transaction_failed"


class SpecificationError(RepositoryException):
    """Raised when a specification cannot be translated to a query expression."""

    default_code = "specification_error"
