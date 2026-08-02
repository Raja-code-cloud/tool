"""Integration tests for repository persistence against PostgreSQL."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any, ClassVar
from uuid import UUID, uuid4

import pytest
from sqlalchemy import DateTime, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository
from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import ConcurrencyConflict
from cloud_content_hub.infrastructure.repositories.sqlalchemy.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.utils import utc_now

pytestmark = pytest.mark.integration

DATABASE_URL = os.getenv("DATABASE_URL")


class IntegrationBase(DeclarativeBase):
    pass


class IntegrationTag(IntegrationBase):
    """Minimal mapped model for repository integration tests."""

    __tablename__ = "integration_repository_tags"

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))

    __mapper_args__: ClassVar[dict[str, Any]] = {"version_id_col": "version"}


@pytest.fixture
async def session_factory() -> async_sessionmaker[AsyncSession]:
    if DATABASE_URL is None:
        pytest.skip("DATABASE_URL is not configured.")

    engine: AsyncEngine = create_async_engine(DATABASE_URL)
    async with engine.begin() as connection:
        await connection.run_sync(IntegrationBase.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    yield factory
    await engine.dispose()


@pytest.mark.asyncio
async def test_repository_crud_and_soft_delete_round_trip(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    workspace_id = uuid4()
    now = utc_now()

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyRepository(
            unit_of_work.session,
            IntegrationTag,
            workspace_scoped=True,
            search_columns=("name",),
            sortable_columns=frozenset({"name", "created_at", "updated_at"}),
        )
        created = await repository.create(
            IntegrationTag(
                id=uuid4(),
                workspace_id=workspace_id,
                name="integration-tag",
                created_at=now,
                updated_at=now,
                version=1,
            )
        )
        fetched = await repository.get_by_id(created.id, workspace_id=workspace_id)
        assert fetched is not None
        assert fetched.name == "integration-tag"

        await repository.soft_delete(
            created.id,
            expected_version=created.version,
            workspace_id=workspace_id,
        )
        assert await repository.get_by_id(created.id, workspace_id=workspace_id) is None

        restored = await repository.restore(
            created.id,
            expected_version=created.version + 1,
            workspace_id=workspace_id,
        )
        assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_repository_detects_concurrency_conflict(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    workspace_id = uuid4()
    now = utc_now()
    entity_id = uuid4()

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyRepository(
            unit_of_work.session,
            IntegrationTag,
            workspace_scoped=True,
        )
        entity = await repository.create(
            IntegrationTag(
                id=entity_id,
                workspace_id=workspace_id,
                name="conflict-tag",
                created_at=now,
                updated_at=now,
                version=1,
            )
        )

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyRepository(
            unit_of_work.session,
            IntegrationTag,
            workspace_scoped=True,
        )
        loaded = await repository.get_by_id(entity.id, workspace_id=workspace_id)
        assert loaded is not None
        loaded.name = "updated"
        await repository.update(loaded, expected_version=loaded.version)

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyRepository(
            unit_of_work.session,
            IntegrationTag,
            workspace_scoped=True,
        )
        stale = await repository.get_by_id(entity.id, workspace_id=workspace_id)
        assert stale is not None
        stale.name = "stale-update"
        with pytest.raises(ConcurrencyConflict):
            await repository.update(stale, expected_version=1)


@pytest.mark.asyncio
async def test_unit_of_work_rolls_back_uncommitted_changes(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    workspace_id = uuid4()
    entity_id = uuid4()
    now = datetime.now(tz=UTC)

    with pytest.raises(RuntimeError, match="rollback"):
        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            repository = SqlAlchemyRepository(
                unit_of_work.session,
                IntegrationTag,
                workspace_scoped=True,
            )
            await repository.create(
                IntegrationTag(
                    id=entity_id,
                    workspace_id=workspace_id,
                    name="rolled-back",
                    created_at=now,
                    updated_at=now,
                    version=1,
                )
            )
            raise RuntimeError("rollback")

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyRepository(
            unit_of_work.session,
            IntegrationTag,
            workspace_scoped=True,
        )
        assert await repository.get_by_id(entity_id, workspace_id=workspace_id) is None
