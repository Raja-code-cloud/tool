# Queries

Queries are immutable dataclasses representing read intent. They never mutate state.

## Shared conventions

- Queries do not carry idempotency keys; reads are inherently safe to repeat.
- All queries are scoped implicitly by `ActorContext.workspace_id`.
- Paged queries return `PagedResultDto[T]` with cursor metadata.

## Assets

### `GetAssetQuery`

```python
@dataclass(frozen=True, slots=True)
class GetAssetQuery:
    asset_id: UUID
```

Returns: `AssetDto`

### `SearchAssetsQuery`

```python
@dataclass(frozen=True, slots=True)
class SearchAssetsQuery:
    query: str
    asset_types: frozenset[AssetType] = frozenset()
    lifecycle_statuses: frozenset[AssetLifecycleStatus] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "relevance"
```

Returns: `PagedResultDto[AssetDto]`

### `ListAssetsQuery`

Structured filter listing without required full-text query.

Returns: `PagedResultDto[AssetDto]`

## Content

### `GetContentQuery`

Returns: `ContentDto`

### `SearchContentQuery` / `ListContentQuery`

Returns: `PagedResultDto[ContentDto]`

## Scheduler

### `GetScheduleQuery`

Returns: `ScheduleDto`

## Analytics

### `GetDashboardQuery`

```python
@dataclass(frozen=True, slots=True)
class GetDashboardQuery:
    period_start: datetime
    period_end: datetime
    time_zone: str = "UTC"
    metric_codes: frozenset[str] = frozenset()
    platform_ids: frozenset[UUID] = frozenset()
```

Returns: `AnalyticsDashboardDto`

Period is validated: `period_end > period_start` and range ≤ 366 days.

## Notifications

### `GetNotificationsQuery`

Recipient-scoped to `actor.user_id`. Supports filters for severity, type code, read state, and date range.

Returns: `PagedResultDto[NotificationDto]`

## Query handler pattern

```python
async def handle(self, actor: ActorContext, query: GetAssetQuery) -> AssetDto:
    require_permission(actor, "assets:read")
    async with self._unit_of_work_factory() as unit_of_work:
        record = await repository.get_by_id(
            workspace_id=actor.workspace_id,
            asset_id=query.asset_id,
        )
    return mapper.to_dto(record)
```

Read-only queries may use a read-only unit of work or a shared session depending on composition-root wiring. Mutations always use a transactional unit of work.
