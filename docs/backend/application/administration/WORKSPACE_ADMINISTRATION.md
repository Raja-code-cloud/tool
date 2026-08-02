# Workspace Administration

## Purpose

Global and workspace administrators manage workspace lifecycle settings and list tenant summaries. Workspace administrators cannot modify global settings.

## Queries

### ListWorkspacesQuery

Returns `PagedResultDto[WorkspaceSummaryResponse]` via `ListWorkspacesHandler`.

Supports filtering by organization, workspace, status, and text query. Global administrators may list all accessible workspaces; workspace administrators are scoped to their assigned workspace.

### ListUsersQuery

Returns `PagedResultDto[UserSummaryResponse]` via `ListUsersHandler`.

Lists users visible within the administrative scope (global or workspace-scoped membership).

## Commands

### UpdateWorkspaceSettingsCommand

```python
@dataclass(frozen=True, slots=True)
class UpdateWorkspaceSettingsCommand:
    workspace_id: UUID
    expected_version: int
    request: UpdateWorkspaceSettingsRequestDto
    idempotency_key: str
```

Mutable fields:

- `name` — workspace display name
- `timeZone` — IANA time zone
- `retentionPolicyDays` — optional retention override

Handler: `UpdateWorkspaceSettingsHandler` returns `WorkspaceSummaryResponse`.

## Authorization

| Operation       | Permission    | Scope               |
| --------------- | ------------- | ------------------- |
| List workspaces | `admin:read`  | Global or workspace |
| List users      | `admin:read`  | Global or workspace |
| Update settings | `admin:write` | Workspace-scoped    |

Global administrators may manage any workspace. Workspace administrators may only update their assigned workspace.

## Business rules

1. At least one mutable field must be provided in update requests.
2. Optimistic concurrency uses the workspace `version` column.
3. Successful updates append audit evidence and publish `WorkspaceUpdated`.
4. Non-secret application configuration is read-only through `IAdministrationRepository.list_application_config`.

## Response DTOs

### WorkspaceSummaryResponse

Extends `ResourceBaseDto` with `organizationId`, `name`, `slug`, `status`, `timeZone`, and optional `retentionPolicyDays`.

### UserSummaryResponse

Extends `ResourceBaseDto` with `email`, `displayName`, `locale`, `timeZone`, and `status`.

## Events

- `WorkspaceUpdated(workspace_id, actor_id, version, occurred_at)`

## Errors

| Error                      | Condition                            |
| -------------------------- | ------------------------------------ |
| `WorkspaceNotFoundError`   | Workspace does not exist             |
| `VersionConflictError`     | Stale optimistic concurrency version |
| `WorkspaceAdminScopeError` | Workspace admin acting outside scope |
| `ValidationError`          | Empty update body                    |
