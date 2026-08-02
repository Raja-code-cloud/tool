"""Shared fixtures for PostgreSQL integration tests."""

from __future__ import annotations

import os
import subprocess
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from cloud_content_hub.infrastructure.database.enums import (
    MembershipStatus,
    OrganizationStatus,
    UserStatus,
    WorkspaceStatus,
)
from cloud_content_hub.infrastructure.database.models.organization import Organization
from cloud_content_hub.infrastructure.database.models.user import User
from cloud_content_hub.infrastructure.database.models.workspace import Workspace
from cloud_content_hub.infrastructure.database.models.workspace_membership import (
    WorkspaceMembership,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.unit_of_work import (
    SqlAlchemyUnitOfWork,
)

pytestmark = pytest.mark.integration

BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _resolve_database_url() -> str | None:
    return os.getenv("DATABASE_URL") or os.getenv("CCH_DATABASE_URL")


@pytest.fixture(scope="session")
def database_url() -> str:
    url = _resolve_database_url()
    if url is None:
        pytest.skip("DATABASE_URL or CCH_DATABASE_URL is not configured.")
    if not url.startswith("postgresql"):
        pytest.skip("Integration tests require a PostgreSQL DATABASE_URL.")
    return url


@pytest.fixture(scope="session")
def migrated_database(database_url: str) -> None:
    """Apply Alembic migrations before adapter integration tests run."""

    environment = os.environ.copy()
    environment["CCH_DATABASE_URL"] = database_url
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=BACKEND_ROOT,
        env=environment,
        check=True,
    )


@pytest.fixture
async def session_factory(
    database_url: str,
    migrated_database: None,
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine: AsyncEngine = create_async_engine(database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    yield factory
    await engine.dispose()


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Minimal tenancy seed for repository adapter tests."""

    organization_id: UUID
    workspace_id: UUID
    user_id: UUID
    membership_id: UUID


@pytest.fixture
async def tenant(session_factory: async_sessionmaker[AsyncSession]) -> TenantContext:
    """Seed organization, workspace, user, and workspace membership."""

    organization_id = uuid4()
    workspace_id = uuid4()
    user_id = uuid4()
    membership_id = uuid4()
    suffix = uuid4().hex[:8]

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        session = unit_of_work.session
        session.add(
            Organization(
                id=organization_id,
                name=f"Adapter Org {suffix}",
                slug=f"adapter-org-{suffix}",
                status=OrganizationStatus.ACTIVE,
                created_by=None,
                updated_by=None,
            )
        )
        session.add(
            User(
                id=user_id,
                email=f"adapter-{suffix}@example.com",
                display_name="Adapter User",
                status=UserStatus.ACTIVE,
                created_by=None,
                updated_by=None,
            )
        )
        session.add(
            Workspace(
                id=workspace_id,
                organization_id=organization_id,
                name=f"Adapter Workspace {suffix}",
                slug=f"adapter-ws-{suffix}",
                status=WorkspaceStatus.ACTIVE,
                created_by=user_id,
                updated_by=user_id,
            )
        )
        session.add(
            WorkspaceMembership(
                id=membership_id,
                workspace_id=workspace_id,
                user_id=user_id,
                status=MembershipStatus.ACTIVE,
                created_by=user_id,
                updated_by=user_id,
            )
        )

    return TenantContext(
        organization_id=organization_id,
        workspace_id=workspace_id,
        user_id=user_id,
        membership_id=membership_id,
    )
