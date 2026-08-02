# RBAC

## Model

RBAC is implemented in `rbac.py` using:

- **Roles** — named collections with optional inheritance
- **Permissions** — stable string codes (for example `content:read`)
- **Permission groups** — expand a permission code into related codes
- **Authorization hooks** — custom async allow/deny decisions
- **AttributePolicy** — ABAC extension point for future resource-aware checks

## Evaluation order

When `Rbac.authorize(principal, permission)` runs:

1. Effective permissions = principal permissions ∪ role permissions (including inheritance and groups)
2. Direct permission match via `Principal.has_permission()`
3. Optional custom `AuthorizationHook`
4. Optional `AttributePolicy`

Denial raises `PermissionDenied` at the dependency layer.

## Wildcards

Permission codes support:

- exact match (`content:read`)
- namespace wildcard (`content:*`)
- global wildcard (`*`)

## FastAPI dependencies

| Dependency                           | Behavior                                |
| ------------------------------------ | --------------------------------------- |
| `CurrentUser`                        | Requires authenticated principal        |
| `OptionalUser`                       | Returns anonymous principal when absent |
| `CurrentAdmin`                       | Requires `admin` role                   |
| `RequireRole("editor")`              | Factory for role enforcement            |
| `RequirePermission("content:write")` | Factory for permission enforcement      |

## Separation from business authorization

Workspace-scoped permissions assigned through membership tables are resolved in application services. Infrastructure RBAC evaluates the authenticated principal's token claims and configured role catalog only.

## Testing utilities

`sample_rbac()` in `testing/fixtures.py` provides inheritance and permission group coverage for unit tests.
