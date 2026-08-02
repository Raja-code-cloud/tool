"""Health contributor registration for the composition root."""

from __future__ import annotations

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from cloud_content_hub.infrastructure.events.factory import (
    EventInfrastructureBundle,
    create_outbox_health_check,
)
from cloud_content_hub.infrastructure.observability.health import (
    ApplicationHealthCheck,
    HealthCheck,
    HealthChecker,
    create_ping_health_check,
)
from cloud_content_hub.infrastructure.storage.interfaces.storage_provider import StorageProvider


def build_health_checker(
    *,
    database_engine: AsyncEngine,
    redis: Redis,
    storage_provider: StorageProvider,
    events: EventInfrastructureBundle,
    session_factory: async_sessionmaker[AsyncSession],
    health_timeout_seconds: float,
) -> HealthChecker:
    """Register all health contributors for the process."""

    checks: list[HealthCheck] = [
        ApplicationHealthCheck(),
        _database_health_check(database_engine),
        _redis_health_check(redis),
        _storage_health_check(storage_provider),
        create_outbox_health_check(events, session_factory=session_factory),
    ]
    return HealthChecker(checks, timeout_seconds=health_timeout_seconds)


def _database_health_check(engine: AsyncEngine) -> HealthCheck:
    async def ping() -> bool:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True

    return create_ping_health_check("database", ping)


def _redis_health_check(redis: Redis) -> HealthCheck:
    async def ping() -> bool:
        return bool(await redis.ping())

    return create_ping_health_check("redis", ping)


def _storage_health_check(storage: StorageProvider) -> HealthCheck:
    async def ping() -> bool:
        result = await storage.health_check()
        return result.healthy

    return create_ping_health_check("storage", ping, degraded_on_failure=True)
