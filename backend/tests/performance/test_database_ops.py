"""Database CRUD, search, and pagination performance validation."""

from __future__ import annotations

from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetSearchCriteria,
    AssetType,
    NewAsset,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.asset_repository import (
    SqlAlchemyAssetRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from tests.integration.conftest import TenantContext
from tests.performance.helpers.metrics import collect_latencies
from tests.performance.helpers.targets import PERFORMANCE_TARGETS, assert_within_target

pytestmark = [pytest.mark.performance, pytest.mark.integration]


@pytest.fixture
async def seeded_assets(
    session_factory: async_sessionmaker[AsyncSession],
    tenant: TenantContext,
) -> TenantContext:
    """Seed a workspace with assets for search and pagination benchmarks."""

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyAssetRepository(unit_of_work.session)
        for index in range(50):
            await repository.create(
                NewAsset(
                    workspace_id=tenant.workspace_id,
                    asset_type=AssetType.ARTICLE if index % 2 == 0 else AssetType.POSTER,
                    title=f"Perf Asset {index:03d}",
                    summary=f"Performance seed asset {index}",
                    owner_id=tenant.user_id,
                    project_id=None,
                    folder_id=None,
                    created_by=tenant.user_id,
                )
            )
    return tenant


@pytest.mark.asyncio
async def test_asset_crud_read_latency(
    session_factory: async_sessionmaker[AsyncSession],
    seeded_assets: TenantContext,
) -> None:
    created_id: UUID | None = None

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyAssetRepository(unit_of_work.session)
        created = await repository.create(
            NewAsset(
                workspace_id=seeded_assets.workspace_id,
                asset_type=AssetType.ARTICLE,
                title="CRUD Latency Asset",
                summary=None,
                owner_id=seeded_assets.user_id,
                project_id=None,
                folder_id=None,
                created_by=seeded_assets.user_id,
            )
        )
        created_id = created.id

    assert created_id is not None

    async def read_once() -> None:
        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            repository = SqlAlchemyAssetRepository(unit_of_work.session)
            fetched = await repository.get_by_id(
                workspace_id=seeded_assets.workspace_id,
                asset_id=created_id,
            )
            assert fetched is not None

    stats = await collect_latencies(
        label="AssetRepository.get_by_id",
        iterations=50,
        operation=read_once,
    )
    assert_within_target(
        stats,
        p95_seconds=PERFORMANCE_TARGETS.db_crud_p95_seconds,
        label="db crud read",
    )


@pytest.mark.asyncio
async def test_asset_search_latency(
    session_factory: async_sessionmaker[AsyncSession],
    seeded_assets: TenantContext,
) -> None:
    async def search_once() -> None:
        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            repository = SqlAlchemyAssetRepository(unit_of_work.session)
            page = await repository.search(
                AssetSearchCriteria(
                    workspace_id=seeded_assets.workspace_id,
                    query="Perf",
                    limit=25,
                )
            )
            assert len(page.items) > 0

    stats = await collect_latencies(
        label="AssetRepository.search",
        iterations=30,
        operation=search_once,
    )
    assert_within_target(
        stats,
        p95_seconds=PERFORMANCE_TARGETS.db_search_p95_seconds,
        label="db search",
    )


@pytest.mark.asyncio
async def test_asset_pagination_latency(
    session_factory: async_sessionmaker[AsyncSession],
    seeded_assets: TenantContext,
) -> None:
    cursor: str | None = None

    async def paginate_once() -> None:
        nonlocal cursor
        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            repository = SqlAlchemyAssetRepository(unit_of_work.session)
            page = await repository.search(
                AssetSearchCriteria(
                    workspace_id=seeded_assets.workspace_id,
                    limit=10,
                    cursor=cursor,
                )
            )
            cursor = page.next_cursor

    stats = await collect_latencies(
        label="AssetRepository.pagination",
        iterations=20,
        operation=paginate_once,
    )
    assert_within_target(
        stats,
        p95_seconds=PERFORMANCE_TARGETS.db_search_p95_seconds,
        label="db pagination",
    )
