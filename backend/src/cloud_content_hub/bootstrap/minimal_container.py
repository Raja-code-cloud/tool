"""Lightweight container used by the HTTP app in local and test environments."""

from __future__ import annotations

from dataclasses import dataclass

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from cloud_content_hub.core.config import Settings
from cloud_content_hub.infrastructure.database.session import (
    create_database_engine,
    create_session_factory,
)


@dataclass(slots=True)
class MinimalContainer:
    settings: Settings
    database_engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    redis: Redis

    @classmethod
    def create(cls, settings: Settings) -> MinimalContainer:
        engine = create_database_engine(settings)
        return cls(
            settings=settings,
            database_engine=engine,
            session_factory=create_session_factory(engine),
            redis=Redis.from_url(
                str(settings.redis_url),
                socket_timeout=settings.redis_timeout_seconds,
                decode_responses=True,
            ),
        )

    async def close(self) -> None:
        await self.redis.aclose()
        await self.database_engine.dispose()
