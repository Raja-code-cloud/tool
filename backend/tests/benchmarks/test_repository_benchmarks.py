"""Repository and database micro-benchmarks."""

from __future__ import annotations

from typing import Any
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

pytestmark = [pytest.mark.benchmark, pytest.mark.integration]


@pytest.fixture
async def benchmark_tenant(
    session_factory: async_sessionmaker[AsyncSession],
    tenant: TenantContext,
) -> tuple[async_sessionmaker[AsyncSession], TenantContext, Any]:
    asset_id = uuid4()
    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyAssetRepository(unit_of_work.session)
        created = await repository.create(
            NewAsset(
                workspace_id=tenant.workspace_id,
                asset_type=AssetType.ARTICLE,
                title="Benchmark Asset",
                summary="Repository benchmark seed",
                owner_id=tenant.user_id,
                project_id=None,
                folder_id=None,
                created_by=tenant.user_id,
            )
        )
        asset_id = created.id
    return session_factory, tenant, asset_id


@pytest.mark.asyncio
async def test_benchmark_asset_get_by_id(
    benchmark: Any,
    benchmark_tenant: tuple[async_sessionmaker[AsyncSession], TenantContext, Any],
) -> None:
    session_factory, tenant, asset_id = benchmark_tenant

    async def run() -> None:
        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            repository = SqlAlchemyAssetRepository(unit_of_work.session)
            fetched = await repository.get_by_id(
                workspace_id=tenant.workspace_id,
                asset_id=asset_id,
            )
            assert fetched is not None

    await benchmark.pedantic(run, rounds=5, iterations=1)


@pytest.mark.asyncio
async def test_benchmark_asset_search(
    benchmark: Any,
    benchmark_tenant: tuple[async_sessionmaker[AsyncSession], TenantContext, Any],
) -> None:
    session_factory, tenant, _asset_id = benchmark_tenant

    async def run() -> None:
        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            repository = SqlAlchemyAssetRepository(unit_of_work.session)
            page = await repository.search(
                AssetSearchCriteria(
                    workspace_id=tenant.workspace_id,
                    query="Benchmark",
                    limit=25,
                )
            )
            assert len(page.items) >= 1

    await benchmark.pedantic(run, rounds=5, iterations=1)
