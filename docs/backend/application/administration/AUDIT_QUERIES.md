# Audit Queries

## Purpose

Administrators query append-only security and material-change audit evidence. Audit logs are immutable; the application module only reads and appends entries.

## Query

### GetAuditSummaryQuery

```python
@dataclass(frozen=True, slots=True)
class GetAuditSummaryQuery:
    workspace_id: UUID | None = None
    organization_id: UUID | None = None
    actions: frozenset[str] = frozenset()
    outcomes: frozenset[AuditOutcome] = frozenset()
    occurred_after: datetime | None = None
    occurred_before: datetime | None = None
    limit: int = 25
```

Handler: `GetAuditSummaryHandler` returns `AuditSummaryResponse`.

## Authorization

Requires `admin:read`. Workspace administrators are scoped to their workspace; global administrators may query across scopes.

## Response

`AuditSummaryResponse` contains:

| Field           | Description                                       |
| --------------- | ------------------------------------------------- |
| `totalCount`    | Total matching audit entries                      |
| `successCount`  | Entries with outcome `success`                    |
| `failureCount`  | Entries with outcome `failure`                    |
| `deniedCount`   | Entries with outcome `denied`                     |
| `recentEntries` | Most recent matching entries (bounded by `limit`) |

Each `AuditEntryDto` exposes safe, redacted fields only: action, target type/id, outcome, source, and timestamp. No secrets, payloads, or full diffs cross the application boundary unless explicitly marked safe in `safe_diff`.

## Audit append (commands)

All administrative commands use `AuditService.record_success` to append immutable audit evidence within the same unit of work as the originating mutation:

| Action                    | Command                          |
| ------------------------- | -------------------------------- |
| `maintenance.enable`      | `EnableMaintenanceModeCommand`   |
| `maintenance.disable`     | `DisableMaintenanceModeCommand`  |
| `role.assign`             | `AssignRoleCommand`              |
| `role.remove`             | `RemoveRoleCommand`              |
| `workspace.update`        | `UpdateWorkspaceSettingsCommand` |
| `provider.health.refresh` | `RefreshProviderHealthCommand`   |

## Repository

`IAdministrationRepository` provides:

- `append_audit(entry: NewAuditLog)` — append-only write
- `get_audit_summary(criteria: AuditSearchCriteria)` — aggregated read

## Data model alignment

Audit logs map to the `audit_logs` table defined in `TABLE_SPECIFICATIONS.md`:

- Scoped by `workspace_id`, `organization_id`, or global source
- Immutable shape enforced at database level
- Retention governed by compliance policy (1–7 years)

## Feature flags (read-only)

Feature flags are boolean settings with keys prefixed `feature.`. `GetFeatureFlagsQuery` returns `tuple[FeatureFlagResponse, ...]` without exposing secret values or internal configuration topology.

Validation ensures flag keys follow the naming convention via `validate_feature_flag_key` when flags are referenced by key.
