"""Shared fixtures for end-to-end workflow tests."""

from __future__ import annotations

import os
import subprocess
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cloud_content_hub.bootstrap.api import create_app
from cloud_content_hub.bootstrap.container import Container
from cloud_content_hub.bootstrap.handlers import wire_handlers
from cloud_content_hub.bootstrap.providers import FixedClock, FixedUuidGenerator
from cloud_content_hub.core.config import Environment, Settings
from cloud_content_hub.infrastructure.events.factory import create_event_infrastructure
from cloud_content_hub.infrastructure.events.testing.fakes import FakeCeleryBroker
from cloud_content_hub.workers.factory import create_worker_bundle

from tests.fixtures.auth import auth_headers, issue_access_token
from tests.fixtures.seed import E2ESeedBundle, seed_e2e_environment

if TYPE_CHECKING:
    from cloud_content_hub.workers.factory import WorkerBundle

pytestmark = [pytest.mark.e2e, pytest.mark.integration]

BACKEND_ROOT = Path(__file__).resolve().parents[2]
FIXED_TIME = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)
FIXED_UUID = UUID("00000000-0000-0000-0000-000000000001")


def _resolve_database_url() -> str | None:
    return os.getenv("DATABASE_URL") or os.getenv("CCH_DATABASE_URL")


def _resolve_redis_url() -> str:
    return os.getenv("CCH_REDIS_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"


@pytest.fixture(scope="session")
def database_url() -> str:
    url = _resolve_database_url()
    if url is None:
        pytest.skip("DATABASE_URL or CCH_DATABASE_URL is not configured.")
    if not url.startswith("postgresql"):
        pytest.skip("E2E tests require a PostgreSQL DATABASE_URL.")
    return url


@pytest.fixture(scope="session")
def migrated_database(database_url: str) -> None:
    """Apply Alembic migrations before E2E tests run."""

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
    from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

    engine: AsyncEngine = create_async_engine(database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    yield factory
    await engine.dispose()


@pytest.fixture
async def e2e_seed(session_factory: async_sessionmaker[AsyncSession]) -> E2ESeedBundle:
    """Seed a complete tenant and catalog for workflow tests."""

    return await seed_e2e_environment(session_factory)


@pytest.fixture
def fake_broker() -> FakeCeleryBroker:
    return FakeCeleryBroker()


@pytest.fixture
def e2e_settings(database_url: str) -> Settings:
    return Settings(
        environment=Environment.TEST,
        database_url=database_url,
        redis_url=_resolve_redis_url(),  # type: ignore[arg-type]
    )


@pytest.fixture
async def e2e_container(
    e2e_settings: Settings,
    fake_broker: FakeCeleryBroker,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[Container]:
    """Process container with deterministic clock, UUIDs, and fake Celery broker."""

    async def noop_startup(_container: Container) -> None:
        return None

    monkeypatch.setattr(
        "cloud_content_hub.bootstrap.startup.startup_application",
        noop_startup,
    )

    container = Container.create(
        e2e_settings,
        clock=FixedClock(FIXED_TIME),
        uuid_generator=FixedUuidGenerator(FIXED_UUID),
    )
    events = create_event_infrastructure(
        broker=fake_broker,
        celery_app=container.celery_app,
        metrics=container.observability.metrics,
        tracer=container.observability.tracer,
    )
    object.__setattr__(container, "events", events)

    yield container

    container.storage_provider.close = _async_noop  # type: ignore[method-assign]
    container.redis.aclose = _async_noop  # type: ignore[method-assign]
    container.database_engine.dispose = _async_noop  # type: ignore[method-assign]
    from cloud_content_hub.bootstrap.shutdown import shutdown_application

    await shutdown_application(container)


async def _async_noop(*_args: object, **_kwargs: object) -> None:
    return None


@pytest.fixture
async def e2e_app(e2e_container: Container, monkeypatch: pytest.MonkeyPatch):
    """FastAPI application wired with real handlers and test infrastructure."""

    async def noop_startup(_container: Container) -> None:
        return None

    monkeypatch.setattr(
        "cloud_content_hub.bootstrap.startup.startup_application",
        noop_startup,
    )

    app = create_app(e2e_container.settings)
    app.state.container = e2e_container
    app.state.handlers = wire_handlers(e2e_container)
    return app


@pytest.fixture
async def auth_client(e2e_app: object, e2e_seed: E2ESeedBundle) -> AsyncIterator[AsyncClient]:
    """Authenticated HTTP client scoped to the seeded workspace."""

    token = issue_access_token(user_id=e2e_seed.user_id)
    transport = ASGITransport(app=e2e_app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers.update(auth_headers(token=token, workspace_id=e2e_seed.workspace_id))
        yield client


@pytest.fixture
def worker_bundle(e2e_container: Container) -> WorkerBundle:
    return create_worker_bundle(e2e_container)


@dataclass(frozen=True, slots=True)
class WorkflowContext:
    """Convenience bundle passed into workflow tests."""

    seed: E2ESeedBundle
    container: Container
    broker: FakeCeleryBroker
    session_factory: async_sessionmaker[AsyncSession]


@pytest.fixture
def workflow_context(
    e2e_seed: E2ESeedBundle,
    e2e_container: Container,
    fake_broker: FakeCeleryBroker,
    session_factory: async_sessionmaker[AsyncSession],
) -> WorkflowContext:
    return WorkflowContext(
        seed=e2e_seed,
        container=e2e_container,
        broker=fake_broker,
        session_factory=session_factory,
    )
