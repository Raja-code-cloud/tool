"""Unit tests for generic SQLAlchemy repository behavior."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository
from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import (
    ConcurrencyConflict,
    EntityNotFound,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.filters import RepositoryFilter
from cloud_content_hub.infrastructure.repositories.sqlalchemy.pagination import PageMetadata
from cloud_content_hub.infrastructure.repositories.sqlalchemy.sorting import SortColumn


class TagLike(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    __tablename__ = "repository_test_tags"

    name: Mapped[str] = mapped_column(String, nullable=False)


@pytest.fixture
def session() -> AsyncMock:
    mock = AsyncMock(spec=AsyncSession)
    mock.add = MagicMock()
    mock.add_all = MagicMock()
    return mock


@pytest.fixture
def repository(session: AsyncMock) -> SqlAlchemyRepository[TagLike]:
    return SqlAlchemyRepository(
        session,
        TagLike,
        workspace_scoped=True,
        search_columns=("name",),
        sortable_columns=frozenset({"name", "created_at", "updated_at"}),
    )


@pytest.mark.asyncio
async def test_create_persists_and_refreshes_entity(
    session: AsyncMock,
    repository: SqlAlchemyRepository[TagLike],
) -> None:
    entity = TagLike(id=uuid4(), workspace_id=uuid4(), name="launch")
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    result = await repository.create(entity)

    session.add.assert_called_once_with(entity)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(entity)
    assert result is entity


@pytest.mark.asyncio
async def test_update_raises_on_version_mismatch(repository: SqlAlchemyRepository[TagLike]) -> None:
    entity = TagLike(id=uuid4(), workspace_id=uuid4(), name="launch", version=2)

    with pytest.raises(ConcurrencyConflict, match="version mismatch"):
        await repository.update(entity, expected_version=1)


@pytest.mark.asyncio
async def test_soft_delete_raises_when_no_rows_updated(
    session: AsyncMock,
    repository: SqlAlchemyRepository[TagLike],
) -> None:
    entity_id = uuid4()
    workspace_id = uuid4()
    execute_result = MagicMock()
    execute_result.rowcount = 0
    session.execute = AsyncMock(return_value=execute_result)

    with pytest.raises(ConcurrencyConflict):
        await repository.soft_delete(
            entity_id,
            expected_version=1,
            workspace_id=workspace_id,
        )


@pytest.mark.asyncio
async def test_delete_raises_when_entity_missing(
    session: AsyncMock,
    repository: SqlAlchemyRepository[TagLike],
) -> None:
    execute_result = MagicMock()
    execute_result.rowcount = 0
    session.execute = AsyncMock(return_value=execute_result)

    with pytest.raises(EntityNotFound):
        await repository.delete(uuid4(), workspace_id=uuid4())


@pytest.mark.asyncio
async def test_find_paginated_returns_page_metadata(
    session: AsyncMock,
    repository: SqlAlchemyRepository[TagLike],
) -> None:
    workspace_id = uuid4()
    entity = TagLike(
        id=uuid4(),
        workspace_id=workspace_id,
        name="launch",
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
        version=1,
    )

    scalars_result = MagicMock()
    scalars_result.all.return_value = [entity]
    session.scalars = AsyncMock(return_value=scalars_result)
    session.scalar = AsyncMock(return_value=1)

    page = await repository.find_paginated(
        page=1,
        page_size=10,
        workspace_id=workspace_id,
        filters=RepositoryFilter(search="launch"),
        sort=[SortColumn(name="name")],
    )

    assert len(page.items) == 1
    assert isinstance(page.metadata, PageMetadata)
    assert page.metadata.total_items == 1


def test_workspace_scoped_repository_requires_workspace_id(
    repository: SqlAlchemyRepository[TagLike],
) -> None:
    with pytest.raises(ValueError, match="workspace_id"):
        repository._build_select(include_deleted=False)
