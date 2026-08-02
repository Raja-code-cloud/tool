"""Unit of work port owned by the application layer."""

from __future__ import annotations

from typing import Protocol, Self


class IUnitOfWork(Protocol):
    """Transaction boundary for a single use case."""

    async def begin(self) -> object:
        """Begin a nested transaction or savepoint."""

    async def commit(self) -> None:
        """Commit the outermost transaction."""

    async def rollback(self) -> None:
        """Rollback the active transaction."""

    async def flush(self) -> None:
        """Flush pending changes without committing."""

    async def __aenter__(self) -> Self:
        """Enter the unit-of-work context."""

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Exit the unit-of-work context, committing or rolling back."""
