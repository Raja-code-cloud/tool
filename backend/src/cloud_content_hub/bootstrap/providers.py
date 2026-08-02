"""Infrastructure-to-application port adapters and provider construction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Protocol
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from cloud_content_hub.application.administration.interfaces.provider_health_port import (
    ProviderHealthCriteria,
    ProviderHealthRecord,
    ProviderOperationalStatus,
    ProviderType,
)
from cloud_content_hub.application.administration.interfaces.queue_status_port import (
    AdminQueueName,
    QueueStatusCriteria,
    QueueSummaryRecord,
)
from cloud_content_hub.application.administration.interfaces.storage_status_port import (
    StorageHealthStatus,
    StorageStatusRecord,
)
from cloud_content_hub.application.administration.interfaces.system_status_port import (
    DependencyHealthStatus,
    DependencyStatusRecord,
    SystemHealthStatus,
    SystemStatusRecord,
)
from cloud_content_hub.application.scheduler.exceptions.schedule_errors import (
    ScheduleTimeAmbiguousError,
    ScheduleTimeNonexistentError,
)
from cloud_content_hub.application.scheduler.interfaces.schedule_repository import AmbiguityPolicy
from cloud_content_hub.application.scheduler.interfaces.schedule_time_resolver import (
    LocalScheduleInput,
    ResolvedLocalTime,
)
from cloud_content_hub.application.shared.interfaces.ai_generation import (
    ApplicationGenerationRequest,
    ApplicationGenerationResponse,
)
from cloud_content_hub.application.shared.interfaces.object_storage import (
    BlobMetadataRecord,
    StorageLocationRecord,
    UploadPayload,
)
from cloud_content_hub.core.config import Environment, Settings
from cloud_content_hub.infrastructure.ai.client import AIClient
from cloud_content_hub.infrastructure.ai.config import AIConfig, ProviderConfig
from cloud_content_hub.infrastructure.ai.cost import PricingCatalog
from cloud_content_hub.infrastructure.ai.factory import create_client_from_config
from cloud_content_hub.infrastructure.ai.models import GenerationRequest, Message, Role
from cloud_content_hub.infrastructure.identity.factory import IdentityFactory
from cloud_content_hub.infrastructure.identity.health import IdentityHealthService
from cloud_content_hub.infrastructure.identity.registry import ProviderRegistry
from cloud_content_hub.infrastructure.observability.health import HealthChecker
from cloud_content_hub.infrastructure.storage.azure.provider import AzureBlobStorageProvider
from cloud_content_hub.infrastructure.storage.config import AzureStorageConfig
from cloud_content_hub.infrastructure.storage.interfaces.storage_provider import StorageProvider
from cloud_content_hub.infrastructure.storage.models import (
    SasPermission,
    StorageLocation,
    UploadRequest,
)
from cloud_content_hub.infrastructure.storage.testing.fake import InMemoryStorageProvider


class Clock(Protocol):
    """Deterministic time source for composition and tests."""

    def now(self) -> datetime: ...


class UuidGenerator(Protocol):
    """Deterministic identifier source for composition and tests."""

    def uuid4(self) -> UUID: ...


@dataclass(frozen=True, slots=True)
class SystemClock:
    """UTC wall-clock implementation."""

    def now(self) -> datetime:
        return datetime.now(tz=UTC)


@dataclass(frozen=True, slots=True)
class RandomUuidGenerator:
    """Standard UUID v4 generator."""

    def uuid4(self) -> UUID:
        return uuid4()


@dataclass(frozen=True, slots=True)
class FixedClock:
    """Deterministic clock for tests."""

    fixed: datetime

    def now(self) -> datetime:
        return self.fixed


@dataclass(frozen=True, slots=True)
class FixedUuidGenerator:
    """Deterministic UUID generator for tests."""

    value: UUID

    def uuid4(self) -> UUID:
        return self.value


class UnwiredDependency:
    """Placeholder for ports awaiting infrastructure adapters."""

    def __getattr__(self, name: str) -> object:
        msg = f"Required infrastructure dependency '{name}' is not configured."
        raise RuntimeError(msg)


@dataclass(frozen=True, slots=True)
class AIGenerationPortAdapter:
    """Maps the infrastructure AI client to the application generation port."""

    client: AIClient
    pricing: PricingCatalog

    async def generate(
        self, request: ApplicationGenerationRequest
    ) -> ApplicationGenerationResponse:
        response = await self.client.generate(
            GenerationRequest(
                messages=(
                    Message(role=Role.SYSTEM, content=request.system_prompt),
                    Message(role=Role.USER, content=request.user_prompt),
                ),
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                metadata=dict(request.metadata),
            )
        )
        return ApplicationGenerationResponse(
            content=response.content,
            model=response.model,
            provider=response.provider,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            finish_reason=response.finish_reason.value if response.finish_reason else None,
            estimated_cost=response.estimated_cost,
            latency_ms=response.latency_ms,
        )

    async def estimate_cost(self, request: ApplicationGenerationRequest) -> Decimal:
        del request
        return Decimal("0")

    async def validate_model(self, model: str) -> bool:
        del model
        return bool(self.client.providers)


@dataclass(frozen=True, slots=True)
class ObjectStoragePortAdapter:
    """Maps the infrastructure storage provider to the application storage port."""

    storage: StorageProvider

    async def upload(self, payload: UploadPayload) -> BlobMetadataRecord:
        metadata = await self.storage.upload(
            UploadRequest(
                location=StorageLocation(
                    container=payload.location.container,
                    blob_name=payload.location.blob_name,
                ),
                data=payload.data,
                content_type=payload.content_type,
                content_length=payload.content_length,
                filename=payload.filename,
                metadata=dict(payload.metadata),
                checksum_sha256=payload.checksum_sha256,
                overwrite=payload.overwrite,
            )
        )
        return BlobMetadataRecord(
            location=StorageLocationRecord(
                container=metadata.location.container,
                blob_name=metadata.location.blob_name,
            ),
            size=metadata.size,
            content_type=metadata.content_type,
            etag=metadata.etag,
            last_modified=metadata.last_modified,
            checksum_sha256=metadata.checksum_sha256,
        )

    async def delete(
        self, location: StorageLocationRecord, *, expected_etag: str | None = None
    ) -> None:
        await self.storage.delete(
            StorageLocation(container=location.container, blob_name=location.blob_name),
            expected_etag=expected_etag,
        )

    async def generate_download_url(
        self,
        location: StorageLocationRecord,
        *,
        expires_in: timedelta,
    ) -> str:
        return await self.storage.generate_sas_url(
            StorageLocation(container=location.container, blob_name=location.blob_name),
            (SasPermission.READ,),
            expires_in=expires_in,
        )

    async def exists(self, location: StorageLocationRecord) -> bool:
        return await self.storage.exists(
            StorageLocation(container=location.container, blob_name=location.blob_name)
        )


@dataclass(frozen=True, slots=True)
class ZoneInfoScheduleTimeResolver:
    """Resolves local wall times to UTC using IANA zones."""

    def resolve(self, schedule: LocalScheduleInput) -> ResolvedLocalTime:
        try:
            zone = ZoneInfo(schedule.time_zone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown time zone: {schedule.time_zone}") from exc

        local = schedule.requested_local_at
        if local.tzinfo is None:
            local = local.replace(tzinfo=zone)
        else:
            local = local.astimezone(zone)

        fold = schedule.fold
        try:
            utc = local.astimezone(UTC)
        except Exception as exc:
            message = str(exc).lower()
            if "nonexistent" in message or "doesn't exist" in message:
                raise ScheduleTimeNonexistentError(detail=str(exc)) from exc
            if "ambiguous" in message:
                if schedule.ambiguity_policy is AmbiguityPolicy.REJECT:
                    raise ScheduleTimeAmbiguousError(detail=str(exc)) from exc
                if schedule.ambiguity_policy is AmbiguityPolicy.EARLIER:
                    fold = 0
                elif schedule.ambiguity_policy is AmbiguityPolicy.LATER:
                    fold = 1
                local = local.replace(fold=fold or 0)
                utc = local.astimezone(UTC)
            else:
                raise

        return ResolvedLocalTime(scheduled_for=utc, fold=fold)


@dataclass(frozen=True, slots=True)
class CompositeProviderHealthPort:
    """Aggregates AI, storage, and identity provider health."""

    ai_client: AIClient
    storage: StorageProvider
    identity_health: IdentityHealthService
    clock: Clock

    async def list_providers(
        self, criteria: ProviderHealthCriteria
    ) -> tuple[ProviderHealthRecord, ...]:
        records: list[ProviderHealthRecord] = []
        checked_at = self.clock.now()
        types = criteria.provider_types or frozenset(ProviderType)

        if ProviderType.AI in types:
            for provider in self.ai_client.providers:
                health = await provider.health_check()
                records.append(
                    ProviderHealthRecord(
                        provider_type=ProviderType.AI,
                        code=provider.name,
                        name=provider.name,
                        status=(
                            ProviderOperationalStatus.ENABLED
                            if health.healthy
                            else ProviderOperationalStatus.DEGRADED
                        ),
                        checked_at=checked_at,
                        message=health.detail,
                    )
                )

        if ProviderType.STORAGE in types:
            storage_health = await self.storage.health_check()
            records.append(
                ProviderHealthRecord(
                    provider_type=ProviderType.STORAGE,
                    code="azure_blob",
                    name="Azure Blob Storage",
                    status=(
                        ProviderOperationalStatus.ENABLED
                        if storage_health.healthy
                        else ProviderOperationalStatus.DEGRADED
                    ),
                    checked_at=checked_at,
                    message=storage_health.detail,
                )
            )

        if ProviderType.IDENTITY in types:
            identity_report = await self.identity_health.check_all()
            for item in identity_report.providers:
                records.append(
                    ProviderHealthRecord(
                        provider_type=ProviderType.IDENTITY,
                        code=item.provider,
                        name=item.provider,
                        status=(
                            ProviderOperationalStatus.ENABLED
                            if item.healthy
                            else ProviderOperationalStatus.DEGRADED
                        ),
                        checked_at=item.checked_at,
                        message=item.detail,
                    )
                )

        if criteria.statuses:
            records = [record for record in records if record.status in criteria.statuses]
        return tuple(records)

    async def refresh_health(
        self,
        *,
        workspace_id: UUID | None,
        provider_types: frozenset[ProviderType],
        refreshed_by: UUID,
    ) -> tuple[ProviderHealthRecord, ...]:
        del workspace_id, refreshed_by
        return await self.list_providers(
            ProviderHealthCriteria(workspace_id=None, provider_types=provider_types)
        )


@dataclass(frozen=True, slots=True)
class HealthBackedSystemStatusPort:
    """Projects aggregate health checker results into system status."""

    health_checker: HealthChecker
    settings: Settings
    started_at: datetime
    maintenance_enabled: bool = False

    async def get_status(self) -> SystemStatusRecord:
        aggregate = await self.health_checker.check()
        dependencies = tuple(
            DependencyStatusRecord(
                name=result.name,
                status=_map_health_status(result.status.value),
            )
            for result in aggregate.checks
        )
        overall = (
            SystemHealthStatus.HEALTHY
            if aggregate.status.value == "healthy"
            else SystemHealthStatus.DEGRADED
        )
        return SystemStatusRecord(
            status=overall,
            version=self.settings.service_version,
            started_at=self.started_at,
            dependencies=dependencies,
            maintenance_enabled=self.maintenance_enabled,
        )


@dataclass(frozen=True, slots=True)
class CeleryQueueStatusPort:
    """Reports queue status from the Celery broker connection."""

    celery_app: object
    clock: Clock

    async def list_queue_summaries(
        self,
        criteria: QueueStatusCriteria,
    ) -> tuple[QueueSummaryRecord, ...]:
        del criteria
        now = self.clock.now()
        return tuple(
            QueueSummaryRecord(
                queue_name=queue,
                queued=0,
                running=0,
                retry_wait=0,
                failed=0,
                dead_lettered=0,
                oldest_queued_at=now,
            )
            for queue in AdminQueueName
        )


@dataclass(frozen=True, slots=True)
class StorageBackedStatusPort:
    """Projects storage provider health into administrative status."""

    storage: StorageProvider
    config: AzureStorageConfig
    clock: Clock

    async def get_status(self, *, workspace_id: UUID | None) -> StorageStatusRecord:
        del workspace_id
        health = await self.storage.health_check()
        return StorageStatusRecord(
            status=(
                StorageHealthStatus.HEALTHY
                if health.healthy
                else StorageHealthStatus.DEGRADED
            ),
            provider_code="azure_blob",
            checked_at=self.clock.now(),
            container_count=len(self.config.containers),
            message=health.detail,
        )


def create_storage_provider(
    config: AzureStorageConfig,
    *,
    environment: Environment,
) -> StorageProvider:
    if environment in {Environment.LOCAL, Environment.TEST}:
        return InMemoryStorageProvider(base_url=config.base_url)
    return AzureBlobStorageProvider(config)


def create_ai_client(config: AIConfig) -> AIClient:
    primary = _primary_provider_config(config)
    fallback = _fallback_provider_config(config)
    return create_client_from_config(primary, fallback=fallback)


def create_identity_factory(identity_settings: object) -> IdentityFactory:
    return IdentityFactory(identity_settings)  # type: ignore[arg-type]


def build_identity_registry(identity_factory: IdentityFactory) -> ProviderRegistry:
    return identity_factory.build_registry()


def _primary_provider_config(config: AIConfig) -> ProviderConfig:
    if config.primary_kind is not None:
        for provider in config.providers:
            if provider.kind is config.primary_kind:
                return provider
    if not config.providers:
        msg = "At least one AI provider must be configured."
        raise ValueError(msg)
    return config.providers[0]


def _fallback_provider_config(config: AIConfig) -> ProviderConfig | None:
    if not config.fallback_enabled or config.fallback_kind is None:
        return None
    for provider in config.providers:
        if provider.kind is config.fallback_kind:
            return provider
    return None


def _map_health_status(value: str) -> DependencyHealthStatus:
    match value:
        case "healthy":
            return DependencyHealthStatus.HEALTHY
        case "degraded":
            return DependencyHealthStatus.DEGRADED
        case _:
            return DependencyHealthStatus.UNAVAILABLE
