"""Administration read model to response DTO mapping."""

from __future__ import annotations

from cloud_content_hub.application.administration.dto.responses import (
    AdminQueueNameDto,
    ApplicationConfigResponse,
    AuditEntryDto,
    AuditOutcomeDto,
    AuditSummaryResponse,
    DependencyHealthStatusDto,
    DependencyStatusDto,
    FeatureFlagResponse,
    MaintenanceModeStateResponse,
    ProviderHealthResponse,
    ProviderOperationalStatusDto,
    ProviderTypeDto,
    QueueStatusResponse,
    StorageHealthStatusDto,
    StorageStatusResponse,
    SystemHealthStatusDto,
    SystemStatusResponse,
    UserStatusDto,
    UserSummaryResponse,
    WorkspaceStatusDto,
    WorkspaceSummaryResponse,
)
from cloud_content_hub.application.administration.interfaces.administration_repository import (
    ApplicationConfigRecord,
    AuditLogRecord,
    AuditSummaryRecord,
    FeatureFlagRecord,
    MaintenanceModeRecord,
    UserRecord,
    WorkspaceRecord,
)
from cloud_content_hub.application.administration.interfaces.provider_health_port import (
    ProviderHealthRecord,
)
from cloud_content_hub.application.administration.interfaces.queue_status_port import (
    QueueSummaryRecord,
)
from cloud_content_hub.application.administration.interfaces.storage_status_port import (
    StorageStatusRecord,
)
from cloud_content_hub.application.administration.interfaces.system_status_port import (
    SystemStatusRecord,
)


class AdministrationMapper:
    """Maps administration read models to response DTOs."""

    @staticmethod
    def to_system_status_dto(record: SystemStatusRecord) -> SystemStatusResponse:
        return SystemStatusResponse(
            status=SystemHealthStatusDto(record.status.value),
            version=record.version,
            started_at=record.started_at,
            dependencies=tuple(
                DependencyStatusDto(
                    name=dependency.name,
                    status=DependencyHealthStatusDto(dependency.status.value),
                )
                for dependency in record.dependencies
            ),
            maintenance_enabled=record.maintenance_enabled,
        )

    @staticmethod
    def to_provider_health_dto(record: ProviderHealthRecord) -> ProviderHealthResponse:
        return ProviderHealthResponse(
            provider_type=ProviderTypeDto(record.provider_type.value),
            code=record.code,
            name=record.name,
            status=ProviderOperationalStatusDto(record.status.value),
            checked_at=record.checked_at,
            message=record.message,
        )

    @staticmethod
    def to_queue_status_dto(record: QueueSummaryRecord) -> QueueStatusResponse:
        return QueueStatusResponse(
            queue_name=AdminQueueNameDto(record.queue_name.value),
            queued=record.queued,
            running=record.running,
            retry_wait=record.retry_wait,
            failed=record.failed,
            dead_lettered=record.dead_lettered,
            oldest_queued_at=record.oldest_queued_at,
        )

    @staticmethod
    def to_storage_status_dto(record: StorageStatusRecord) -> StorageStatusResponse:
        return StorageStatusResponse(
            status=StorageHealthStatusDto(record.status.value),
            provider_code=record.provider_code,
            checked_at=record.checked_at,
            container_count=record.container_count,
            message=record.message,
        )

    @staticmethod
    def to_user_summary_dto(record: UserRecord) -> UserSummaryResponse:
        return UserSummaryResponse(
            id=record.id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            email=record.email,
            display_name=record.display_name,
            locale=record.locale,
            time_zone=record.time_zone,
            status=UserStatusDto(record.status.value),
        )

    @staticmethod
    def to_workspace_summary_dto(record: WorkspaceRecord) -> WorkspaceSummaryResponse:
        return WorkspaceSummaryResponse(
            id=record.id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            organization_id=record.organization_id,
            name=record.name,
            slug=record.slug,
            status=WorkspaceStatusDto(record.status.value),
            time_zone=record.time_zone,
            retention_policy_days=record.retention_policy_days,
        )

    @staticmethod
    def to_audit_entry_dto(record: AuditLogRecord) -> AuditEntryDto:
        return AuditEntryDto(
            id=record.id,
            workspace_id=record.workspace_id,
            organization_id=record.organization_id,
            actor_user_id=record.actor_user_id,
            action=record.action,
            target_type=record.target_type,
            target_id=record.target_id,
            outcome=AuditOutcomeDto(record.outcome.value),
            source=record.source,
            occurred_at=record.occurred_at,
        )

    @staticmethod
    def to_audit_summary_dto(record: AuditSummaryRecord) -> AuditSummaryResponse:
        return AuditSummaryResponse(
            total_count=record.total_count,
            success_count=record.success_count,
            failure_count=record.failure_count,
            denied_count=record.denied_count,
            recent_entries=tuple(
                AdministrationMapper.to_audit_entry_dto(entry) for entry in record.recent_entries
            ),
        )

    @staticmethod
    def to_feature_flag_dto(record: FeatureFlagRecord) -> FeatureFlagResponse:
        return FeatureFlagResponse(
            key=record.key,
            enabled=record.enabled,
            description=record.description,
            owner=record.owner,
            purpose=record.purpose,
            expires_at=record.expires_at,
        )

    @staticmethod
    def to_application_config_dto(record: ApplicationConfigRecord) -> ApplicationConfigResponse:
        return ApplicationConfigResponse(
            key=record.key,
            value=record.value,
            value_type=record.value_type,
            scope_type=record.scope_type.value,
            description=record.description,
        )

    @staticmethod
    def to_maintenance_mode_dto(record: MaintenanceModeRecord) -> MaintenanceModeStateResponse:
        return MaintenanceModeStateResponse(
            enabled=record.enabled,
            message=record.message,
            updated_at=record.updated_at,
            updated_by=record.updated_by,
        )
