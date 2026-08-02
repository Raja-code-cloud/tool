"""Unit of work coordinating repository persistence boundaries."""

from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction, async_sessionmaker

from cloud_content_hub.infrastructure.repositories.sqlalchemy.transaction import TransactionManager


class SqlAlchemyUnitOfWork:
    """Async unit of work that owns session and transaction boundaries."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._transaction: TransactionManager | None = None

    @property
    def session(self) -> AsyncSession:
        """Return the active session for repository implementations."""

        if self._session is None:
            raise RuntimeError("Unit of work has not been entered.")
        return self._session

    @property
    def transaction(self) -> TransactionManager:
        """Return the active transaction manager."""

        if self._transaction is None:
            raise RuntimeError("Unit of work has not been entered.")
        return self._transaction

    async def begin(self) -> AsyncSessionTransaction:
        """Begin a nested transaction or savepoint."""

        return await self.transaction.begin()

    async def commit(self) -> None:
        """Commit the outermost transaction."""

        await self.transaction.commit()

    async def rollback(self) -> None:
        """Rollback the active transaction."""

        await self.transaction.rollback()

    async def flush(self) -> None:
        """Flush pending changes without committing."""

        await self.transaction.flush()

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        await self._session.__aenter__()
        self._transaction = TransactionManager(self._session)
        await self._transaction.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return

        try:
            if exc_type is not None:
                await self.rollback()
            elif self._transaction is not None and self._transaction.depth == 1:
                await self.commit()
        finally:
            await self._session.__aexit__(exc_type, exc_value, traceback)
            self._session = None
            self._transaction = None
