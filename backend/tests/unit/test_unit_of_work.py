"""Unit tests for unit-of-work and transaction management."""

from __future__ import annotations

from types import TracebackType
from typing import Self
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import TransactionFailed
from cloud_content_hub.infrastructure.repositories.sqlalchemy.transaction import TransactionManager
from cloud_content_hub.infrastructure.repositories.sqlalchemy.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


class FakeTransaction:
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


@pytest.mark.asyncio
async def test_transaction_manager_rolls_back_on_exception() -> None:
    session = AsyncMock(spec=AsyncSession)
    session.begin = AsyncMock(return_value=FakeTransaction())
    session.rollback = AsyncMock()
    session.commit = AsyncMock()

    manager = TransactionManager(session)
    with pytest.raises(RuntimeError, match="boom"):
        async with manager:
            raise RuntimeError("boom")

    session.rollback.assert_awaited()


@pytest.mark.asyncio
async def test_transaction_manager_commit_requires_active_transaction() -> None:
    manager = TransactionManager(AsyncMock(spec=AsyncSession))
    with pytest.raises(TransactionFailed, match="No active transaction"):
        await manager.commit()


@pytest.mark.asyncio
async def test_unit_of_work_commits_on_success() -> None:
    session = AsyncMock(spec=AsyncSession)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.begin = AsyncMock(return_value=FakeTransaction())
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    factory = MagicMock(spec=async_sessionmaker[AsyncSession])
    factory.return_value = session

    async with SqlAlchemyUnitOfWork(factory) as unit_of_work:
        assert unit_of_work.session is session

    session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_unit_of_work_rolls_back_on_failure() -> None:
    session = AsyncMock(spec=AsyncSession)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.begin = AsyncMock(return_value=FakeTransaction())
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    factory = MagicMock(spec=async_sessionmaker[AsyncSession])
    factory.return_value = session

    with pytest.raises(RuntimeError, match="failure"):
        async with SqlAlchemyUnitOfWork(factory):
            raise RuntimeError("failure")

    session.rollback.assert_awaited()
