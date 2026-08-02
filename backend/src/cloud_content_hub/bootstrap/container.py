"""Dependency injection container for the Cloud Content Hub composition root."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from celery import Celery
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from cloud_content_hub.core.config import Settings

if TYPE_CHECKING:
    from cloud_content_hub.application.administration.interfaces.provider_health_port import (
        IProviderHealthPort,
    )
    from cloud_content_hub.application.administration.interfaces.queue_status_port import (
        IQueueStatusPort,
    )
    from cloud_content_hub.application.administration.interfaces.storage_status_port import (
        IStorageStatusPort,
    )
    from cloud_content_hub.application.administration.interfaces.system_status_port import (
        ISystemStatusPort,
    )
    from cloud_content_hub.application.scheduler.interfaces.schedule_time_resolver import (
        IScheduleTimeResolver,
    )
    from cloud_content_hub.application.shared.interfaces.ai_generation import AIGenerationPort
    from cloud_content_hub.application.shared.interfaces.object_storage import IObjectStoragePort
    from cloud_content_hub.bootstrap.configuration import BootstrapConfiguration
    from cloud_content_hub.bootstrap.providers import Clock, UuidGenerator
    from cloud_content_hub.bootstrap.repositories import RepositoryFactories
    from cloud_content_hub.bootstrap.services import ApplicationServices
    from cloud_content_hub.infrastructure.ai.client import AIClient
    from cloud_content_hub.infrastructure.events.factory import EventInfrastructureBundle
    from cloud_content_hub.infrastructure.identity.factory import IdentityFactory
    from cloud_content_hub.infrastructure.identity.health import IdentityHealthService
    from cloud_content_hub.infrastructure.identity.registry import ProviderRegistry
    from cloud_content_hub.infrastructure.observability.factory import ObservabilityBundle
    from cloud_content_hub.infrastructure.observability.health import HealthChecker
    from cloud_content_hub.infrastructure.storage.interfaces.storage_provider import StorageProvider


@dataclass(slots=True)
class Container:
    """Process-scoped dependency injection container."""

    settings: Settings
    configuration: BootstrapConfiguration
    started_at: datetime
    database_engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    redis: Redis
    celery_app: Celery
    observability: ObservabilityBundle
    events: EventInfrastructureBundle
    identity_factory: IdentityFactory
    identity_registry: ProviderRegistry
    identity_health: IdentityHealthService
    storage_provider: StorageProvider
    ai_client: AIClient
    ai_generation_port: AIGenerationPort
    object_storage_port: IObjectStoragePort
    provider_health_port: IProviderHealthPort
    system_status_port: ISystemStatusPort
    queue_status_port: IQueueStatusPort
    storage_status_port: IStorageStatusPort
    schedule_time_resolver: IScheduleTimeResolver
    clock: Clock
    uuid_generator: UuidGenerator
    repositories: RepositoryFactories
    services: ApplicationServices
    health_checker: HealthChecker

    @classmethod
    def create(
        cls,
        settings: Settings,
        *,
        clock: Clock | None = None,
        uuid_generator: UuidGenerator | None = None,
    ) -> Container:
        """Construct the full process container from typed settings."""

        from cloud_content_hub.bootstrap.configuration import load_bootstrap_configuration
        from cloud_content_hub.bootstrap.events import create_event_bundle
        from cloud_content_hub.bootstrap.health import build_health_checker
        from cloud_content_hub.bootstrap.providers import (
            AIGenerationPortAdapter,
            CeleryQueueStatusPort,
            CompositeProviderHealthPort,
            HealthBackedSystemStatusPort,
            ObjectStoragePortAdapter,
            RandomUuidGenerator,
            StorageBackedStatusPort,
            SystemClock,
            ZoneInfoScheduleTimeResolver,
            build_identity_registry,
            create_ai_client,
            create_identity_factory,
            create_storage_provider,
        )
        from cloud_content_hub.bootstrap.repositories import create_repository_factories
        from cloud_content_hub.bootstrap.services import create_application_services
        from cloud_content_hub.bootstrap.worker import create_celery_app
        from cloud_content_hub.infrastructure.ai.cost import PricingCatalog
        from cloud_content_hub.infrastructure.database.session import (
            create_database_engine,
            create_session_factory,
        )
        from cloud_content_hub.infrastructure.identity.health import IdentityHealthService
        from cloud_content_hub.infrastructure.observability.factory import (
            create_observability_bundle,
        )

        configuration = load_bootstrap_configuration(settings)
        resolved_clock = clock or SystemClock()
        resolved_uuid_generator = uuid_generator or RandomUuidGenerator()
        started_at = resolved_clock.now()

        engine = create_database_engine(settings)
        session_factory = create_session_factory(engine)
        redis = Redis.from_url(
            str(settings.redis_url),
            socket_timeout=settings.redis_timeout_seconds,
            decode_responses=True,
        )
        celery_app = create_celery_app(settings)
        observability = create_observability_bundle(configuration.observability)
        events = create_event_bundle(celery_app=celery_app, observability=observability)

        identity_factory = create_identity_factory(configuration.identity)
        identity_registry = build_identity_registry(identity_factory)
        identity_health = IdentityHealthService(identity_registry)

        storage_provider = create_storage_provider(
            configuration.storage,
            environment=settings.environment,
        )
        ai_client = create_ai_client(configuration.ai)
        ai_generation_port = AIGenerationPortAdapter(ai_client, PricingCatalog())
        object_storage_port = ObjectStoragePortAdapter(storage_provider)

        repositories = create_repository_factories(session_factory)
        services = create_application_services(
            repositories=repositories,
            ai_generation_port=ai_generation_port,
        )

        provider_health_port = CompositeProviderHealthPort(
            ai_client=ai_client,
            storage=storage_provider,
            identity_health=identity_health,
            clock=resolved_clock,
        )
        queue_status_port = CeleryQueueStatusPort(celery_app=celery_app, clock=resolved_clock)
        storage_status_port = StorageBackedStatusPort(
            storage=storage_provider,
            config=configuration.storage,
            clock=resolved_clock,
        )
        schedule_time_resolver = ZoneInfoScheduleTimeResolver()

        health_checker = build_health_checker(
            database_engine=engine,
            redis=redis,
            storage_provider=storage_provider,
            events=events,
            session_factory=session_factory,
            health_timeout_seconds=configuration.observability.health_timeout_seconds,
        )
        system_status_port = HealthBackedSystemStatusPort(
            health_checker=health_checker,
            settings=settings,
            started_at=started_at,
        )

        return cls(
            settings=settings,
            configuration=configuration,
            started_at=started_at,
            database_engine=engine,
            session_factory=session_factory,
            redis=redis,
            celery_app=celery_app,
            observability=observability,
            events=events,
            identity_factory=identity_factory,
            identity_registry=identity_registry,
            identity_health=identity_health,
            storage_provider=storage_provider,
            ai_client=ai_client,
            ai_generation_port=ai_generation_port,
            object_storage_port=object_storage_port,
            provider_health_port=provider_health_port,
            system_status_port=system_status_port,
            queue_status_port=queue_status_port,
            storage_status_port=storage_status_port,
            schedule_time_resolver=schedule_time_resolver,
            clock=resolved_clock,
            uuid_generator=resolved_uuid_generator,
            repositories=repositories,
            services=services,
            health_checker=health_checker,
        )

    async def startup(self) -> None:
        """Initialize and verify external dependencies."""

        from cloud_content_hub.bootstrap.startup import startup_application

        await startup_application(self)

    async def close(self) -> None:
        """Gracefully release process-scoped resources."""

        from cloud_content_hub.bootstrap.shutdown import shutdown_application

        await shutdown_application(self)
