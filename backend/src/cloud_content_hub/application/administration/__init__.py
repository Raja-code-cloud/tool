"""Administration application module."""

from cloud_content_hub.application.administration.dto.responses import (
    AuditSummaryResponse,
    FeatureFlagResponse,
    ProviderHealthResponse,
    QueueStatusResponse,
    SystemStatusResponse,
    UserSummaryResponse,
    WorkspaceSummaryResponse,
)
from cloud_content_hub.application.administration.handlers import (
    update_workspace_settings_handler as workspace_settings_handlers,
)
from cloud_content_hub.application.administration.handlers.assign_role_handler import (
    AssignRoleHandler,
)
from cloud_content_hub.application.administration.handlers.disable_maintenance_mode_handler import (
    DisableMaintenanceModeHandler,
)
from cloud_content_hub.application.administration.handlers.enable_maintenance_mode_handler import (
    EnableMaintenanceModeHandler,
)
from cloud_content_hub.application.administration.handlers.get_ai_providers_handler import (
    GetAIProvidersHandler,
)
from cloud_content_hub.application.administration.handlers.get_audit_summary_handler import (
    GetAuditSummaryHandler,
)
from cloud_content_hub.application.administration.handlers.get_feature_flags_handler import (
    GetFeatureFlagsHandler,
)
from cloud_content_hub.application.administration.handlers.get_identity_providers_handler import (
    GetIdentityProvidersHandler,
)
from cloud_content_hub.application.administration.handlers.get_provider_health_handler import (
    GetProviderHealthHandler,
)
from cloud_content_hub.application.administration.handlers.get_queue_status_handler import (
    GetQueueStatusHandler,
)
from cloud_content_hub.application.administration.handlers.get_storage_status_handler import (
    GetStorageStatusHandler,
)
from cloud_content_hub.application.administration.handlers.get_system_status_handler import (
    GetSystemStatusHandler,
)
from cloud_content_hub.application.administration.handlers.list_users_handler import (
    ListUsersHandler,
)
from cloud_content_hub.application.administration.handlers.list_workspaces_handler import (
    ListWorkspacesHandler,
)
from cloud_content_hub.application.administration.handlers.refresh_provider_health_handler import (
    RefreshProviderHealthHandler,
)
from cloud_content_hub.application.administration.handlers.remove_role_handler import (
    RemoveRoleHandler,
)

UpdateWorkspaceSettingsHandler = workspace_settings_handlers.UpdateWorkspaceSettingsHandler

__all__ = [
    "AssignRoleHandler",
    "AuditSummaryResponse",
    "DisableMaintenanceModeHandler",
    "EnableMaintenanceModeHandler",
    "FeatureFlagResponse",
    "GetAIProvidersHandler",
    "GetAuditSummaryHandler",
    "GetFeatureFlagsHandler",
    "GetIdentityProvidersHandler",
    "GetProviderHealthHandler",
    "GetQueueStatusHandler",
    "GetStorageStatusHandler",
    "GetSystemStatusHandler",
    "ListUsersHandler",
    "ListWorkspacesHandler",
    "ProviderHealthResponse",
    "QueueStatusResponse",
    "RefreshProviderHealthHandler",
    "RemoveRoleHandler",
    "SystemStatusResponse",
    "UpdateWorkspaceSettingsHandler",
    "UserSummaryResponse",
    "WorkspaceSummaryResponse",
]
