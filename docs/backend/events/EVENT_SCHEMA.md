# Event Schema

## Envelope

Events are serialized to JSON using a versioned envelope:

```json
{
  "schema_version": 1,
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "asset.uploaded",
  "event_version": 1,
  "aggregate_type": "asset",
  "aggregate_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "workspace_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c9",
  "organization_id": null,
  "occurred_at": "2026-01-01T12:00:00+00:00",
  "payload": {},
  "metadata": {
    "correlation_id": "corr-123",
    "trace_id": "abc123",
    "span_id": "def456",
    "request_id": "req-789",
    "source": "cloud_content_hub",
    "content_type": "application/json"
  },
  "headers": {
    "correlation_id": "corr-123",
    "trace_id": "abc123",
    "traceparent": "00-abc123-def456-01"
  }
}
```

| Field            | Description                                                   |
| ---------------- | ------------------------------------------------------------- |
| `schema_version` | Top-level envelope version (`EVENT_SCHEMA_VERSION`)           |
| `event_id`       | Outbox row UUID; use for idempotency                          |
| `event_type`     | Past-tense dotted name (for example `notification.created`)   |
| `event_version`  | Payload schema version, independent of aggregate `version`    |
| `aggregate_type` | Stable aggregate classifier (`asset`, `content`, `global`, …) |
| `aggregate_id`   | Aggregate identifier                                          |
| `occurred_at`    | Domain timestamp from the raising handler                     |
| `payload`        | Redacted JSON snapshot of the domain event                    |
| `metadata`       | Cross-cutting identifiers for logs and traces                 |
| `headers`        | Propagation carrier stored on the outbox row                  |

## Database mapping

| Envelope field      | `outbox_events` column                                        |
| ------------------- | ------------------------------------------------------------- |
| `event_id`          | `id`                                                          |
| `event_type`        | `event_type`                                                  |
| `event_version`     | `event_version`                                               |
| `aggregate_type`    | `aggregate_type`                                              |
| `aggregate_id`      | `aggregate_id`                                                |
| `workspace_id`      | `workspace_id`                                                |
| `organization_id`   | `organization_id`                                             |
| `payload`           | `payload` (JSONB)                                             |
| `headers`           | `headers` (JSONB)                                             |
| `occurred_at`       | `occurred_at`                                                 |
| dispatch scheduling | `available_at`, `attempt_count`, `last_error`, `published_at` |

## Event catalog

### Assets

| Event class     | `event_type`     | `aggregate_type` |
| --------------- | ---------------- | ---------------- |
| `AssetUploaded` | `asset.uploaded` | `asset`          |
| `AssetDeleted`  | `asset.deleted`  | `asset`          |
| `AssetReplaced` | `asset.replaced` | `asset`          |
| `AssetRestored` | `asset.restored` | `asset`          |

### Content

| Event class          | `event_type`          | `aggregate_type` |
| -------------------- | --------------------- | ---------------- |
| `ContentGenerated`   | `content.generated`   | `content`        |
| `ContentRegenerated` | `content.regenerated` | `content`        |
| `ContentArchived`    | `content.archived`    | `content`        |
| `ContentDeleted`     | `content.deleted`     | `content`        |
| `ContentApproved`    | `content.approved`    | `content`        |
| `ContentRejected`    | `content.rejected`    | `content`        |

### Notifications

| Event class            | `event_type`                       | `aggregate_type`           |
| ---------------------- | ---------------------------------- | -------------------------- |
| `NotificationCreated`  | `notification.created`             | `notification`             |
| `NotificationRead`     | `notification.read`                | `notification`             |
| `NotificationArchived` | `notification.archived`            | `notification`             |
| `NotificationDeleted`  | `notification.deleted`             | `notification`             |
| `PreferencesUpdated`   | `notification.preferences_updated` | `notification_preferences` |

### Analytics

| Event class                 | `event_type`                          | `aggregate_type` |
| --------------------------- | ------------------------------------- | ---------------- |
| `AnalyticsExportRequested`  | `analytics.export_requested`          | `analytics`      |
| `DashboardCacheRefreshed`   | `analytics.dashboard_cache_refreshed` | `analytics`      |
| `AnalyticsSnapshotArchived` | `analytics.snapshot_archived`         | `analytics`      |

### Administration

| Event class               | `event_type`                               | `aggregate_type` |
| ------------------------- | ------------------------------------------ | ---------------- |
| `MaintenanceModeEnabled`  | `administration.maintenance_mode_enabled`  | `global`         |
| `MaintenanceModeDisabled` | `administration.maintenance_mode_disabled` | `global`         |
| `RoleAssigned`            | `administration.role_assigned`             | `membership`     |
| `RoleRemoved`             | `administration.role_removed`              | `membership`     |
| `WorkspaceUpdated`        | `administration.workspace_updated`         | `workspace`      |
| `ProviderHealthChecked`   | `administration.provider_health_checked`   | `provider`       |

## Payload rules

- Dataclass fields serialize to JSON-safe scalars (`datetime` → ISO-8601, `UUID` → string, enums → value).
- No secrets, tokens, raw provider payloads, or cross-tenant identifiers beyond the event scope.
- Consumers must treat `(event_id)` or `(aggregate_id, event_type, occurred_at)` as dedupe keys where needed.

## Versioning

- Increment `event_version` when adding required payload fields or changing semantics.
- Never mutate historical outbox rows; consumers must tolerate unknown fields and support multiple `event_version` values during rollout.
