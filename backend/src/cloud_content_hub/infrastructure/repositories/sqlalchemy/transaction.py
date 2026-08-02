"""Transaction management with savepoints and automatic rollback."""

from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import TransactionFailed


class TransactionManager:
    """Manage nested transactions and savepoints for a single session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._transaction: AsyncSessionTransaction | None = None
        self._depth = 0

    @property
    def depth(self) -> int:
        """Return the current nested transaction depth."""

        return self._depth

    async def begin(self) -> AsyncSessionTransaction:
        """Begin a transaction or nested savepoint."""

        if self._transaction is None:
            self._transaction = await self._session.begin()
            self._depth = 1
            return self._transaction

        nested = await self._session.begin_nested()
        self._depth += 1
        return nested

    async def commit(self) -> None:
        """Commit the outermost transaction."""

        if self._transaction is None:
            raise TransactionFailed("No active transaction to commit.")
        try:
            await self._session.commit()
        except Exception as exc:
            raise TransactionFailed("Commit failed.") from exc
        finally:
            self._transaction = None
            self._depth = 0

    async def rollback(self) -> None:
        """Rollback the current transaction or savepoint."""

        if self._transaction is None:
            return
        await self._session.rollback()
        self._transaction = None
        self._depth = 0

    async def flush(self) -> None:
        """Flush pending changes without committing."""

        await self._session.flush()

    async def __aenter__(self) -> Self:
        await self.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
            return
        if self._depth > 1:
            await self._session.commit()
            self._depth -= 1
            return
        await self.commit()
