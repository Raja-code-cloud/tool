# Service Registration

## Container-owned components

`Container.create(settings)` registers the following process-scoped services:

| Component                   | Factory / constructor                        | Lifetime           |
| --------------------------- | -------------------------------------------- | ------------------ |
| `Settings`                  | Passed in                                    | Process            |
| `BootstrapConfiguration`    | `load_bootstrap_configuration()`             | Process, immutable |
| `AsyncEngine`               | `create_database_engine()`                   | Process            |
| `async_sessionmaker`        | `create_session_factory()`                   | Process            |
| `Redis`                     | `Redis.from_url()`                           | Process            |
| `Celery`                    | `create_celery_app()`                        | Process            |
| `ObservabilityBundle`       | `create_observability_bundle()`              | Process            |
| `EventInfrastructureBundle` | `create_event_bundle()`                      | Process            |
| `IdentityFactory`           | `create_identity_factory()`                  | Process            |
| `ProviderRegistry`          | `identity_factory.build_registry()`          | Process            |
| `IdentityHealthService`     | wraps registry                               | Process            |
| `StorageProvider`           | `create_storage_provider()`                  | Process            |
| `AIClient`                  | `create_ai_client()`                         | Process            |
| `AIGenerationPort`          | `AIGenerationPortAdapter`                    | Process            |
| `IObjectStoragePort`        | `ObjectStoragePortAdapter`                   | Process            |
| Admin status ports          | See `providers.py`                           | Process            |
| `IScheduleTimeResolver`     | `ZoneInfoScheduleTimeResolver`               | Process            |
| `Clock`                     | `SystemClock` (overridable in tests)         | Process            |
| `UuidGenerator`             | `RandomUuidGenerator` (overridable in tests) | Process            |
| `RepositoryFactories`       | `create_repository_factories()`              | Process            |
| `ApplicationServices`       | `create_application_services()`              | Process            |
| `HealthChecker`             | `build_health_checker()`                     | Process            |

## Repository factories

`RepositoryFactories` exposes callables for:

- `SqlAlchemyUnitOfWork`
- Administration, analytics, asset, content (+ generation request/output), notification (+ preferences), publication, and schedule repositories

Each repository factory receives the active unit of work and returns an implementation bound to its session.

## Application services

| Service                     | Dependencies                                                         |
| --------------------------- | -------------------------------------------------------------------- |
| `AuditService`              | `administration_repository_factory`                                  |
| `ContentGenerationService`  | `AIGenerationPort`, `ContentPromptService`, `PlatformMappingService` |
| `DuplicateDetectionService` | Default policy only                                                  |

## Handler registry keys

`wire_handlers(container)` registers delivery keys including:

| Key                                                                                          | Handler                 |
| -------------------------------------------------------------------------------------------- | ----------------------- |
| `list_assets`, `search_assets`, `get_asset`, `upload_asset`, `replace_asset`, `delete_asset` | Asset handlers          |
| `list_content`, `get_content`, `generate_content`, `regenerate_content`, …                   | Content handlers        |
| `create_publication`, `dispatch_publication`, `cancel_publication`                           | Publishing handlers     |
| `create_schedule`, `get_schedule`, `cancel_schedule`                                         | Scheduler handlers      |
| `get_analytics_dashboard`, `list_analytics_posts`, …                                         | Analytics handlers      |
| `list_notifications`, `mark_notification_read`, `delete_notification`                        | Notification handlers   |
| `list_admin_queues`, `list_admin_providers`, `get_admin_system_status`                       | Administration handlers |

## Test overrides

Tests may pass alternate `clock` and `uuid_generator` implementations to `Container.create()` for deterministic behavior without changing production wiring.
