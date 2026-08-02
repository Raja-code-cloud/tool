"""Domain event registration, naming, and serialization."""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Mapping
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar
from uuid import NAMESPACE_URL, UUID, uuid5

from cloud_content_hub.infrastructure.events.exceptions import (
    EventSerializationError,
    UnknownEventTypeError,
)
from cloud_content_hub.infrastructure.events.import_utils import preload_repository_module

EventT = TypeVar("EventT")
ScopeResolver = Callable[[object], tuple[UUID | None, UUID | None, str, UUID]]
PayloadSerializer = Callable[[object], dict[str, Any]]

GLOBAL_AGGREGATE_ID = UUID("00000000-0000-0000-0000-000000000001")
DEFAULT_EVENT_VERSION = 1


@dataclasses.dataclass(frozen=True, slots=True)
class EventDescriptor:
    """Registration metadata for one domain event variant."""

    event_type: str
    event_version: int
    aggregate_type: str
    resolve_scope: ScopeResolver
    serialize_payload: PayloadSerializer
    celery_queue: str


def _workspace_scope(
    event: object,
    *,
    aggregate_type: str,
    aggregate_id_attr: str,
) -> tuple[UUID | None, UUID | None, str, UUID]:
    workspace_id = getattr(event, "workspace_id", None)
    aggregate_id = getattr(event, aggregate_id_attr)
    if not isinstance(workspace_id, UUID) or not isinstance(aggregate_id, UUID):
        msg = f"Event {type(event).__name__} is missing required scope fields."
        raise EventSerializationError(msg)
    return workspace_id, None, aggregate_type, aggregate_id


def _global_scope(_event: object) -> tuple[UUID | None, UUID | None, str, UUID]:
    return None, None, "global", GLOBAL_AGGREGATE_ID


def _provider_health_scope(event: object) -> tuple[UUID | None, UUID | None, str, UUID]:
    provider_code = getattr(event, "provider_code", None)
    if not isinstance(provider_code, str):
        msg = "ProviderHealthChecked is missing provider_code."
        raise EventSerializationError(msg)
    aggregate_id = uuid5(NAMESPACE_URL, f"provider:{provider_code}")
    return None, None, "provider", aggregate_id


def _serialize_dataclass(event: object) -> dict[str, Any]:
    if not dataclasses.is_dataclass(event):
        msg = f"Expected dataclass event, got {type(event)!r}."
        raise EventSerializationError(msg)
    payload: dict[str, Any] = _json_safe(dataclasses.asdict(event))  # type: ignore[arg-type]
    return payload


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_json_safe(item) for item in value]
    if isinstance(value, set | frozenset):
        return [_json_safe(item) for item in value]
    return value


class EventRegistry:
    """Maps domain event classes to outbox metadata and serializers."""

    def __init__(self) -> None:
        self._by_type: dict[type[object], EventDescriptor] = {}
        self._by_name: dict[str, EventDescriptor] = {}

    def register(self, event_class: type[EventT], descriptor: EventDescriptor) -> None:
        self._by_type[event_class] = descriptor
        self._by_name[descriptor.event_type] = descriptor

    def describe(self, event: object) -> EventDescriptor:
        descriptor = self._by_type.get(type(event))
        if descriptor is None:
            raise UnknownEventTypeError(f"Unregistered event type: {type(event)!r}")
        return descriptor

    def describe_by_name(self, event_type: str) -> EventDescriptor:
        descriptor = self._by_name.get(event_type)
        if descriptor is None:
            raise UnknownEventTypeError(f"Unknown event_type: {event_type!r}")
        return descriptor

    def serialize(self, event: object) -> OutboxSerialization:
        descriptor = self.describe(event)
        workspace_id, organization_id, aggregate_type, aggregate_id = descriptor.resolve_scope(
            event
        )
        payload = descriptor.serialize_payload(event)
        return OutboxSerialization(
            workspace_id=workspace_id,
            organization_id=organization_id,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=descriptor.event_type,
            event_version=descriptor.event_version,
            payload=payload,
            celery_queue=descriptor.celery_queue,
        )


@dataclasses.dataclass(frozen=True, slots=True)
class OutboxSerialization:
    """Resolved outbox metadata for one domain event."""

    workspace_id: UUID | None
    organization_id: UUID | None
    aggregate_type: str
    aggregate_id: UUID
    event_type: str
    event_version: int
    payload: dict[str, Any]
    celery_queue: str


def create_default_registry() -> EventRegistry:
    """Build the registry covering all supported application domain events."""

    preload_repository_module(
        "application/assets/interfaces/asset_repository.py",
        "cloud_content_hub.application.assets.interfaces.asset_repository",
    )
    preload_repository_module(
        "application/content/interfaces/content_repository.py",
        "cloud_content_hub.application.content.interfaces.content_repository",
    )
    preload_repository_module(
        "application/notifications/interfaces/notification_repository.py",
        "cloud_content_hub.application.notifications.interfaces.notification_repository",
    )
    preload_repository_module(
        "application/administration/interfaces/provider_health_port.py",
        "cloud_content_hub.application.administration.interfaces.provider_health_port",
    )

    from cloud_content_hub.application.administration.events import (
        MaintenanceModeDisabled,
        MaintenanceModeEnabled,
        ProviderHealthChecked,
        RoleAssigned,
        RoleRemoved,
        WorkspaceUpdated,
    )
    from cloud_content_hub.application.analytics.events import (
        AnalyticsExportRequested,
        AnalyticsSnapshotArchived,
        DashboardCacheRefreshed,
    )
    from cloud_content_hub.application.assets.events import (
        AssetDeleted,
        AssetReplaced,
        AssetRestored,
        AssetUploaded,
    )
    from cloud_content_hub.application.content.events import (
        ContentApproved,
        ContentArchived,
        ContentDeleted,
        ContentGenerated,
        ContentRegenerated,
        ContentRejected,
    )
    from cloud_content_hub.application.notifications.events import (
        NotificationArchived,
        NotificationCreated,
        NotificationDeleted,
        NotificationRead,
        PreferencesUpdated,
    )

    registry = EventRegistry()

    def register_asset(event_class: type[object], event_type: str, aggregate_id_attr: str) -> None:
        registry.register(
            event_class,
            EventDescriptor(
                event_type=event_type,
                event_version=DEFAULT_EVENT_VERSION,
                aggregate_type="asset",
                resolve_scope=lambda event: _workspace_scope(
                    event, aggregate_type="asset", aggregate_id_attr=aggregate_id_attr
                ),
                serialize_payload=_serialize_dataclass,
                celery_queue="media",
            ),
        )

    register_asset(AssetUploaded, "asset.uploaded", "asset_id")
    register_asset(AssetDeleted, "asset.deleted", "asset_id")
    register_asset(AssetReplaced, "asset.replaced", "asset_id")
    register_asset(AssetRestored, "asset.restored", "asset_id")

    def register_content(
        event_class: type[object], event_type: str, aggregate_id_attr: str = "content_id"
    ) -> None:
        registry.register(
            event_class,
            EventDescriptor(
                event_type=event_type,
                event_version=DEFAULT_EVENT_VERSION,
                aggregate_type="content",
                resolve_scope=lambda event: _workspace_scope(
                    event, aggregate_type="content", aggregate_id_attr=aggregate_id_attr
                ),
                serialize_payload=_serialize_dataclass,
                celery_queue="ai",
            ),
        )

    register_content(ContentGenerated, "content.generated")
    register_content(ContentRegenerated, "content.regenerated")
    register_content(ContentArchived, "content.archived")
    register_content(ContentDeleted, "content.deleted")
    register_content(ContentApproved, "content.approved")
    register_content(ContentRejected, "content.rejected")

    def register_notification(event_class: type[object], event_type: str) -> None:
        registry.register(
            event_class,
            EventDescriptor(
                event_type=event_type,
                event_version=DEFAULT_EVENT_VERSION,
                aggregate_type="notification",
                resolve_scope=lambda event: _workspace_scope(
                    event, aggregate_type="notification", aggregate_id_attr="notification_id"
                ),
                serialize_payload=_serialize_dataclass,
                celery_queue="notification",
            ),
        )

    register_notification(NotificationCreated, "notification.created")
    register_notification(NotificationRead, "notification.read")
    register_notification(NotificationArchived, "notification.archived")
    register_notification(NotificationDeleted, "notification.deleted")
    registry.register(
        PreferencesUpdated,
        EventDescriptor(
            event_type="notification.preferences_updated",
            event_version=DEFAULT_EVENT_VERSION,
            aggregate_type="notification_preferences",
            resolve_scope=lambda event: _workspace_scope(
                event, aggregate_type="notification_preferences", aggregate_id_attr="user_id"
            ),
            serialize_payload=_serialize_dataclass,
            celery_queue="notification",
        ),
    )

    def register_analytics(
        event_class: type[object], event_type: str, aggregate_id_attr: str
    ) -> None:
        registry.register(
            event_class,
            EventDescriptor(
                event_type=event_type,
                event_version=DEFAULT_EVENT_VERSION,
                aggregate_type="analytics",
                resolve_scope=lambda event: _workspace_scope(
                    event, aggregate_type="analytics", aggregate_id_attr=aggregate_id_attr
                ),
                serialize_payload=_serialize_dataclass,
                celery_queue="maintenance",
            ),
        )

    register_analytics(AnalyticsExportRequested, "analytics.export_requested", "export_id")
    register_analytics(
        DashboardCacheRefreshed, "analytics.dashboard_cache_refreshed", "workspace_id"
    )
    register_analytics(AnalyticsSnapshotArchived, "analytics.snapshot_archived", "snapshot_id")

    registry.register(
        MaintenanceModeEnabled,
        EventDescriptor(
            event_type="administration.maintenance_mode_enabled",
            event_version=DEFAULT_EVENT_VERSION,
            aggregate_type="global",
            resolve_scope=_global_scope,
            serialize_payload=_serialize_dataclass,
            celery_queue="maintenance",
        ),
    )
    registry.register(
        MaintenanceModeDisabled,
        EventDescriptor(
            event_type="administration.maintenance_mode_disabled",
            event_version=DEFAULT_EVENT_VERSION,
            aggregate_type="global",
            resolve_scope=_global_scope,
            serialize_payload=_serialize_dataclass,
            celery_queue="maintenance",
        ),
    )
    registry.register(
        RoleAssigned,
        EventDescriptor(
            event_type="administration.role_assigned",
            event_version=DEFAULT_EVENT_VERSION,
            aggregate_type="membership",
            resolve_scope=lambda event: _workspace_scope(
                event, aggregate_type="membership", aggregate_id_attr="membership_id"
            ),
            serialize_payload=_serialize_dataclass,
            celery_queue="maintenance",
        ),
    )
    registry.register(
        RoleRemoved,
        EventDescriptor(
            event_type="administration.role_removed",
            event_version=DEFAULT_EVENT_VERSION,
            aggregate_type="membership",
            resolve_scope=lambda event: _workspace_scope(
                event, aggregate_type="membership", aggregate_id_attr="membership_id"
            ),
            serialize_payload=_serialize_dataclass,
            celery_queue="maintenance",
        ),
    )
    registry.register(
        WorkspaceUpdated,
        EventDescriptor(
            event_type="administration.workspace_updated",
            event_version=DEFAULT_EVENT_VERSION,
            aggregate_type="workspace",
            resolve_scope=lambda event: _workspace_scope(
                event, aggregate_type="workspace", aggregate_id_attr="workspace_id"
            ),
            serialize_payload=_serialize_dataclass,
            celery_queue="maintenance",
        ),
    )
    registry.register(
        ProviderHealthChecked,
        EventDescriptor(
            event_type="administration.provider_health_checked",
            event_version=DEFAULT_EVENT_VERSION,
            aggregate_type="provider",
            resolve_scope=_provider_health_scope,
            serialize_payload=_serialize_dataclass,
            celery_queue="maintenance",
        ),
    )

    return registry
