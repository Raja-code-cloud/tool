# Administration Module

The administration application module coordinates operational monitoring, tenant administration, role management, audit queries, and global maintenance controls.

## Layout

```text
application/administration/
├── commands/          # Write intent (maintenance, roles, workspace settings)
├── queries/           # Read intent (status, users, workspaces, audit, flags)
├── handlers/          # One handler per use case
├── dto/               # Request and response DTOs
├── validators/        # Authorization and business validation
├── interfaces/        # Repository and provider ports
├── mappers/           # Read model → response DTO mapping
├── exceptions/        # Feature-specific application errors
├── services/          # Cross-cutting orchestration (audit)
└── events/            # Domain events for administrative mutations
```

## Permissions

| Operation class      | Permission                              |
| -------------------- | --------------------------------------- |
| Queries              | `admin:read`                            |
| Commands             | `admin:write`                           |
| Global-only commands | `admin:*` or `*` (global administrator) |

Workspace administrators may manage users, roles, and workspace settings within their assigned workspace. They cannot modify global settings such as maintenance mode or refresh global provider health without global administrator privileges.

## Use cases

### Queries

| Use case           | Handler                       | Returns                                    |
| ------------------ | ----------------------------- | ------------------------------------------ |
| System status      | `GetSystemStatusHandler`      | `SystemStatusResponse`                     |
| Provider health    | `GetProviderHealthHandler`    | `tuple[ProviderHealthResponse, ...]`       |
| Queue status       | `GetQueueStatusHandler`       | `tuple[QueueStatusResponse, ...]`          |
| Storage status     | `GetStorageStatusHandler`     | `StorageStatusResponse`                    |
| Identity providers | `GetIdentityProvidersHandler` | `tuple[ProviderHealthResponse, ...]`       |
| AI providers       | `GetAIProvidersHandler`       | `tuple[ProviderHealthResponse, ...]`       |
| List users         | `ListUsersHandler`            | `PagedResultDto[UserSummaryResponse]`      |
| List workspaces    | `ListWorkspacesHandler`       | `PagedResultDto[WorkspaceSummaryResponse]` |
| Audit summary      | `GetAuditSummaryHandler`      | `AuditSummaryResponse`                     |
| Feature flags      | `GetFeatureFlagsHandler`      | `tuple[FeatureFlagResponse, ...]`          |

### Commands

| Use case                  | Handler                          | Returns                              |
| ------------------------- | -------------------------------- | ------------------------------------ |
| Enable maintenance mode   | `EnableMaintenanceModeHandler`   | `MaintenanceModeStateResponse`       |
| Disable maintenance mode  | `DisableMaintenanceModeHandler`  | `MaintenanceModeStateResponse`       |
| Assign role               | `AssignRoleHandler`              | `None`                               |
| Remove role               | `RemoveRoleHandler`              | `None`                               |
| Update workspace settings | `UpdateWorkspaceSettingsHandler` | `WorkspaceSummaryResponse`           |
| Refresh provider health   | `RefreshProviderHealthHandler`   | `tuple[ProviderHealthResponse, ...]` |

## Ports

| Port                            | Purpose                                                          |
| ------------------------------- | ---------------------------------------------------------------- |
| `IAdministrationRepository`     | Users, workspaces, roles, audit, feature flags, maintenance mode |
| `ISystemStatusPort`             | Aggregate system and dependency health                           |
| `IProviderHealthPort`           | Provider health query and refresh                                |
| `IQueueStatusPort`              | Queue depth and terminal state summaries                         |
| `IStorageStatusPort`            | Storage subsystem health                                         |
| `IAdministrationEventPublisher` | Transactional outbox for domain events                           |

## Events

All mutating use cases append audit evidence and publish domain events:

- `MaintenanceModeEnabled` / `MaintenanceModeDisabled`
- `RoleAssigned` / `RoleRemoved`
- `WorkspaceUpdated`
- `ProviderHealthChecked`

## Related documentation

- [`SYSTEM_STATUS.md`](SYSTEM_STATUS.md)
- [`ROLE_MANAGEMENT.md`](ROLE_MANAGEMENT.md)
- [`WORKSPACE_ADMINISTRATION.md`](WORKSPACE_ADMINISTRATION.md)
- [`AUDIT_QUERIES.md`](AUDIT_QUERIES.md)
