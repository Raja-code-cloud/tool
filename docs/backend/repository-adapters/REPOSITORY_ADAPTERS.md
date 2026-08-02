# Repository Adapters

## Purpose

SQLAlchemy repository adapters implement application repository ports under
`backend/src/cloud_content_hub/infrastructure/repositories/sqlalchemy/`. Each adapter
translates ORM rows into application read models and applies persistence mechanics
(filtering, pagination, sorting, workspace isolation, optimistic locking, soft delete)
without embedding business rules.

## Layout

```text
infrastructure/repositories/sqlalchemy/
├── adapter_session.py          # Resolve AsyncSession from IUnitOfWork
├── base.py                     # Generic SqlAlchemyRepository
├── cursor_pagination.py        # Keyset cursor helpers for application ports
├── unit_of_work.py             # SqlAlchemyUnitOfWork (commit boundary)
├── asset_repository.py         # IAssetRepository
├── content_repository.py       # IContentRepository, generation ports
├── publication_repository.py   # IPublicationRepository
├── schedule_repository.py      # IScheduleRepository
├── analytics_repository.py     # IAnalyticsRepository
├── notification_repository.py  # INotificationRepository, preference port
├── administration_repository.py# IAdministrationRepository
└── user_repository.py          # User listing helper (composed by administration)
```

## Adapter responsibilities

| Adapter                                      | Port                                | Primary ORM models                                                      |
| -------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------- |
| `SqlAlchemyAssetRepository`                  | `IAssetRepository`                  | `ContentAsset`, `StorageObject`, `AssetStorageObject`                   |
| `SqlAlchemyContentRepository`                | `IContentRepository`                | `ContentAsset`, `ContentDraft`, `ContentVersion`                        |
| `SqlAlchemyGenerationRequestRepository`      | `IGenerationRequestRepository`      | `AIGenerationRequest`                                                   |
| `SqlAlchemyGenerationOutputRepository`       | `IGenerationOutputRepository`       | `AIGenerationOutput`                                                    |
| `SqlAlchemyPublicationRepository`            | `IPublicationRepository`            | `Publication`, `PublicationTarget`                                      |
| `SqlAlchemyScheduleRepository`               | `IScheduleRepository`               | `PublicationSchedule`                                                   |
| `SqlAlchemyAnalyticsRepository`              | `IAnalyticsRepository`              | `AnalyticsSnapshot`, `MetricObservation`, `ContentPerformanceSnapshot`  |
| `SqlAlchemyNotificationRepository`           | `INotificationRepository`           | `Notification`, `NotificationType`                                      |
| `SqlAlchemyNotificationPreferenceRepository` | `INotificationPreferenceRepository` | `NotificationPreference`                                                |
| `SqlAlchemyAdministrationRepository`         | `IAdministrationRepository`         | `Workspace`, `Setting`, `AuditLog`, composes `SqlAlchemyUserRepository` |
| `SqlAlchemyUserRepository`                   | (helper)                            | `User`, `WorkspaceMembership`                                           |

## Construction and wiring

Adapters accept an `AsyncSession` directly. The composition root resolves the session
from the active unit of work:

```python
from cloud_content_hub.infrastructure.repositories.sqlalchemy.adapter_session import resolve_session
from cloud_content_hub.infrastructure.repositories.sqlalchemy.asset_repository import (
    SqlAlchemyAssetRepository,
)

def asset_repository_factory(uow: IUnitOfWork) -> IAssetRepository:
    return SqlAlchemyAssetRepository(resolve_session(uow))
```

Factory registration lives in `bootstrap/repositories.py`.

## Translation rules

- **Read models only**: adapters return application dataclass records, never ORM instances.
- **Workspace isolation**: every tenant-owned query includes an explicit `workspace_id` predicate.
- **Soft delete**: active reads filter `deleted_at IS NULL` unless the port exposes an
  administrative deleted-row accessor (for example `get_deleted_by_id`).
- **Optimistic locking**: mutating operations pass `expected_version` to the generic repository
  or perform a version-checked update; conflicts surface as `ConcurrencyConflict`.
- **No commits**: adapters flush when needed but never call `session.commit()`. The unit of work
  owns transaction boundaries.

## Domain-specific mapping notes

### Content aggregate

- Application `content_id` maps to `ContentAsset.id`.
- Draft body lives in `content_drafts`; `content_version_id` maps from `draft.base_version_id`.
- `set_current_version` updates the draft pointer rather than mutating immutable version rows.

### Publications

- ORM `Publication.version_id` maps to application `content_version_id`.

### Generation outputs

- Approve/reject review state is stored in `output_metadata["status"]` to respect immutable
  output row constraints.

### Administration settings

- Maintenance mode uses setting key `system.maintenance_mode`.
- Feature flags use prefix `feature.`.

### Analytics

- Metric filtering and date-range delta enrichment are implemented locally in the adapter layer
  (no application service imports).

## Testing

PostgreSQL integration tests live in
`backend/tests/integration/test_sqlalchemy_repository_adapters.py`. They require
`DATABASE_URL` or `CCH_DATABASE_URL`, apply Alembic migrations, and exercise adapter
round-trips through `SqlAlchemyUnitOfWork`.

Run:

```bash
cd backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cloud_content_hub \
  pytest tests/integration/test_sqlalchemy_repository_adapters.py -m integration
```

## Related documentation

- Generic repository pattern: `docs/backend/repositories/REPOSITORY_PATTERN.md`
- Query and pagination strategy: `docs/backend/repository-adapters/QUERY_STRATEGY.md`
- ORM schema: `docs/backend/database/`
