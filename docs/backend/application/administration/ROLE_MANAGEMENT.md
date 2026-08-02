# Role Management

## Purpose

Administrators assign and remove workspace roles through membership junction records. All changes generate audit evidence and domain events.

## Commands

### AssignRoleCommand

```python
@dataclass(frozen=True, slots=True)
class AssignRoleCommand:
    request: AssignRoleRequestDto  # workspace_id, membership_id, role_id
    idempotency_key: str
```

Handler: `AssignRoleHandler`

### RemoveRoleCommand

```python
@dataclass(frozen=True, slots=True)
class RemoveRoleCommand:
    request: RemoveRoleRequestDto  # workspace_id, membership_id, role_id
    idempotency_key: str
```

Handler: `RemoveRoleHandler`

## Authorization

Both commands require `admin:write`. Workspace administrators are scoped to their assigned workspace via `validate_workspace_admin_scope`.

Global administrators (`admin:*` or `*`) bypass role hierarchy checks.

## Business rules

1. The target membership must exist in the requested workspace.
2. The target role must be a system role or belong to the same workspace.
3. The actor's highest assigned role rank must meet or exceed the target role rank.
4. Only administrators (rank ≥ 90) may assign or remove system roles.
5. All successful mutations append an audit log and publish `RoleAssigned` or `RoleRemoved`.

## Role hierarchy

| Code            | Rank |
| --------------- | ---- |
| `owner`         | 100  |
| `admin`         | 90   |
| `billing_admin` | 85   |
| `editor`        | 50   |
| `reviewer`      | 40   |
| `viewer`        | 10   |
| `member`        | 5    |

Custom workspace roles default to rank 0 unless explicitly ranked.

## Repository operations

| Method             | Purpose                                    |
| ------------------ | ------------------------------------------ |
| `get_membership`   | Validate membership exists                 |
| `get_role`         | Load target role                           |
| `list_actor_roles` | Resolve actor's current roles in workspace |
| `assign_role`      | Create membership_roles junction row       |
| `remove_role`      | Delete membership_roles junction row       |
| `append_audit`     | Record security evidence                   |

## Events

- `RoleAssigned(workspace_id, membership_id, role_id, actor_id, occurred_at)`
- `RoleRemoved(workspace_id, membership_id, role_id, actor_id, occurred_at)`

## Errors

| Error                         | Condition                            |
| ----------------------------- | ------------------------------------ |
| `MembershipNotFoundError`     | Membership does not exist            |
| `RoleNotFoundError`           | Role does not exist                  |
| `RoleHierarchyViolationError` | Actor rank insufficient              |
| `WorkspaceAdminScopeError`    | Workspace admin acting outside scope |
