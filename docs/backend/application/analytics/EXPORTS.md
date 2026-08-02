# Analytics Exports

## Overview

Export requests are orchestrated asynchronously. The application module validates the request, estimates row count, persists the export record, and raises `AnalyticsExportRequested`. Background workers (out of scope) perform the actual file generation and delivery.

## RequestAnalyticsExport

**Command:** `RequestAnalyticsExportCommand`

**Request:** `AnalyticsExportRequestDto`

| Field          | Type                     | Notes                                                  |
| -------------- | ------------------------ | ------------------------------------------------------ |
| `export_type`  | `str`                    | Export category (e.g. `posts`, `platforms`, `summary`) |
| `format`       | `ExportFormatRequestDto` | `csv` or `json`, default `csv`                         |
| `period_start` | `datetime`               | Export period start                                    |
| `period_end`   | `datetime`               | Export period end                                      |
| `platform_ids` | `tuple[UUID, ...]`       | Optional platform filter                               |
| `metric_codes` | `tuple[str, ...]`        | Optional metric filter                                 |

**Returns:** `AnalyticsExportResponse`

Includes export `id`, `status` (initially `queued`), `format`, period, `requested_at`, and optional `row_estimate`.

## Validation and limits

`ExportOrchestrationService` coordinates validation:

1. Validate period (ordered, ≤ 366 days)
2. Validate metric codes against allowlist
3. Validate platform ownership when platforms are specified
4. Call `IAnalyticsRepository.estimate_export_rows`
5. Reject when estimate exceeds **100,000 rows** (`AnalyticsExportLimitError`)

The command carries an `idempotency_key` for delivery-layer deduplication; handler logic remains idempotent through repository semantics.

## Event

`AnalyticsExportRequested` is published within the same unit of work:

```python
@dataclass(frozen=True, slots=True)
class AnalyticsExportRequested:
    workspace_id: UUID
    export_id: UUID
    export_type: str
    actor_id: UUID
    period_start: datetime
    period_end: datetime
    occurred_at: datetime
```

Workers subscribe to this event (via outbox) to enqueue export jobs. The application module does not implement job execution, file storage, or download URL generation.

## ArchiveAnalyticsSnapshot

**Command:** `ArchiveAnalyticsSnapshotCommand`

Archives a cached analytics snapshot by ID. Workspace-scoped through `NewArchivedSnapshot.workspace_id`. Raises `AnalyticsSnapshotNotFoundError` when the snapshot does not exist in the workspace.

Publishes `AnalyticsSnapshotArchived` on success.

## Import analytics (legacy)

`ImportAnalyticsCommand` persists manually imported observations through `IAnalyticsRepository.import_observations`. External platform API ingestion is out of scope; this command supports controlled observation import for testing or manual backfill.

## Permissions

All export and snapshot commands require `analytics:read` per current workspace RBAC configuration. Delivery layers may map export endpoints to additional scopes in future API revisions.
