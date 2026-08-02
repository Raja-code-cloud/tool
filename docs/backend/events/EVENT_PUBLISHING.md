# Event Publishing

## Overview

The event publishing infrastructure implements the application-layer publisher ports for assets, content, notifications, analytics, and administration. Each adapter serializes a domain event, enriches headers with correlation and trace context, and appends one row to `outbox_events` through the caller's unit of work.

## Publisher ports

| Port                            | Adapter                        | Domain events                                                                                                                   |
| ------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `IAssetEventPublisher`          | `AssetEventPublisher`          | `AssetUploaded`, `AssetDeleted`, `AssetReplaced`, `AssetRestored`                                                               |
| `IContentEventPublisher`        | `ContentEventPublisher`        | `ContentGenerated`, `ContentRegenerated`, `ContentArchived`, `ContentDeleted`, `ContentApproved`, `ContentRejected`             |
| `INotificationEventPublisher`   | `NotificationEventPublisher`   | `NotificationCreated`, `NotificationRead`, `NotificationArchived`, `NotificationDeleted`, `PreferencesUpdated`                  |
| `IAnalyticsEventPublisher`      | `AnalyticsEventPublisher`      | `AnalyticsExportRequested`, `DashboardCacheRefreshed`, `AnalyticsSnapshotArchived`                                              |
| `IAdministrationEventPublisher` | `AdministrationEventPublisher` | `MaintenanceModeEnabled`, `MaintenanceModeDisabled`, `RoleAssigned`, `RoleRemoved`, `WorkspaceUpdated`, `ProviderHealthChecked` |

## Wiring

Use `create_event_infrastructure()` at the composition root:

```python
from cloud_content_hub.infrastructure.events import create_event_infrastructure

bundle = create_event_infrastructure(metrics=metrics, tracer=tracer)

upload_handler = UploadAssetHandler(
    unit_of_work_factory=uow_factory,
    asset_repository_factory=asset_repo_factory,
    job_repository_factory=job_repo_factory,
    event_publisher=bundle.publishers.assets,
)
```

Content handlers that receive a factory use a lambda:

```python
event_publisher_factory=lambda uow: bundle.publishers.content
```

## Handler contract

1. Perform repository mutations inside the active unit of work.
2. Call `await event_publisher.publish(event, unit_of_work=unit_of_work)` **before** `flush()`.
3. Never call Celery, HTTP, or provider SDKs from the handler transaction.

## Observability

Publisher adapters automatically capture:

- `correlation_id` and `request_id` from request context variables
- Active OpenTelemetry trace and span identifiers
- W3C `traceparent` / `tracestate` propagation headers

Structured logs use the `outbox_event_enqueued` and `outbox_event_delivered` events in the dispatcher and delivery service.

## Configuration

`EventPublishingConfig` controls batch size, retry limits, backoff, poison-message threshold, Celery task name, and default queue. Override at bootstrap time for environment-specific tuning.

## Testing

Use `FakeCeleryBroker` and `RecordingPlatformDeliverer` from `infrastructure/events/testing/` for unit tests. Application handler tests should inject publisher fakes or the real adapters against a test database session.
