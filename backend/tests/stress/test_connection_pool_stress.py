"""Database connection pool and query stress validation."""

from __future__ import annotations

from uuid import uuid4

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
from tests.performance.helpers.metrics import run_concurrent

pytestmark = [pytest.mark.stress, pytest.mark.performance, pytest.mark.integration]


@pytest.fixture
async def stress_tenant(
    session_factory: async_sessionmaker[AsyncSession],
    tenant: TenantContext,
) -> tuple[async_sessionmaker[AsyncSession], TenantContext]:
    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyAssetRepository(unit_of_work.session)
        for index in range(100):
            await repository.create(
                NewAsset(
                    workspace_id=tenant.workspace_id,
                    asset_type=AssetType.POSTER,
                    title=f"Stress Asset {index:03d}",
                    summary=f"Connection pool stress seed {index}",
                    owner_id=tenant.user_id,
                    project_id=None,
                    folder_id=None,
                    created_by=tenant.user_id,
                )
            )
    return session_factory, tenant


@pytest.mark.asyncio
async def test_concurrent_search_connection_pressure(
    stress_tenant: tuple[async_sessionmaker[AsyncSession], TenantContext],
) -> None:
    session_factory, tenant = stress_tenant

    async def search_once() -> None:
        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            repository = SqlAlchemyAssetRepository(unit_of_work.session)
            page = await repository.search(
                AssetSearchCriteria(
                    workspace_id=tenant.workspace_id,
                    query="Stress",
                    limit=25,
                    sort="-updated_at",
                )
            )
            assert len(page.items) > 0

    stats = await run_concurrent(concurrency=20, per_worker=5, operation=search_once)
    assert stats.count == 100
    assert stats.p99 < 2.0


@pytest.mark.asyncio
async def test_concurrent_crud_reads(
    stress_tenant: tuple[async_sessionmaker[AsyncSession], TenantContext],
) -> None:
    session_factory, tenant = stress_tenant
    asset_id = uuid4()

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyAssetRepository(unit_of_work.session)
        created = await repository.create(
            NewAsset(
                workspace_id=tenant.workspace_id,
                asset_type=AssetType.ARTICLE,
                title="Pool Stress Target",
                summary=None,
                owner_id=tenant.user_id,
                project_id=None,
                folder_id=None,
                created_by=tenant.user_id,
            )
        )
        asset_id = created.id

    async def read_once() -> None:
        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            repository = SqlAlchemyAssetRepository(unit_of_work.session)
            fetched = await repository.get_by_id(
                workspace_id=tenant.workspace_id,
                asset_id=asset_id,
            )
            assert fetched is not None

    stats = await run_concurrent(concurrency=30, per_worker=5, operation=read_once)
    assert stats.p95 < 1.0
