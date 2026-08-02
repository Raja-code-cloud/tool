# Dependencies

FastAPI dependencies for the delivery layer are defined in `api/dependencies.py`.

## Infrastructure dependencies

| Dependency             | Purpose                                                                 |
| ---------------------- | ----------------------------------------------------------------------- |
| `get_container`        | Resolves the process `Container` or `MinimalContainer` from `app.state` |
| `get_settings`         | Typed `Settings` from the container                                     |
| `get_database_session` | Async SQLAlchemy session scope                                          |
| `get_redis`            | Redis client                                                            |

## Identity and authorization

| Dependency                                      | Purpose                                                            |
| ----------------------------------------------- | ------------------------------------------------------------------ |
| `CurrentUser`                                   | Re-exported authenticated `Principal` from identity infrastructure |
| `require_permission(code)`                      | Returns a FastAPI dependency enforcing a stable permission code    |
| `require_workspace_id` / `WorkspaceId`          | Parses required `X-Workspace-ID` header                            |
| `optional_workspace_id` / `OptionalWorkspaceId` | Optional workspace header for admin routes                         |
| `get_actor` / `Actor`                           | Builds `ActorContext` for workspace-scoped routes                  |
| `get_admin_actor` / `AdminActor`                | Builds `ActorContext` for admin routes                             |

`ActorContext` is the only identity object passed to application handlers.

## Concurrency and idempotency headers

| Dependency        | Header            | Rule                                      |
| ----------------- | ----------------- | ----------------------------------------- |
| `IfMatch`         | `If-Match`        | Required positive integer ETag            |
| `OptionalIfMatch` | `If-Match`        | Optional ETag                             |
| `IdempotencyKey`  | `Idempotency-Key` | 8–128 printable non-whitespace characters |

## Handler registry

```python
@dataclass(slots=True)
class HandlerRegistry:
    handlers: dict[str, Any]

    def resolve(self, name: str) -> Any: ...
```

Each router declares typed handler dependencies via:

```python
GetAssetHandlerDep = Annotated[GetAssetHandler, Depends(handler_dependency("get_asset"))]
```

Tests register mocks:

```python
app.state.handlers = HandlerRegistry(handlers={"get_asset": mock_handler})
```

Production startup (non-test environments) uses `bootstrap/handlers.wire_handlers(container)` to populate the registry.

## Typical endpoint dependency stack

```python
async def get_asset(
    asset_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("assets:read"))],
    handler: GetAssetHandlerDep,
) -> JSONResponse:
    ...
```

1. Path/query validation (FastAPI + Pydantic)
2. Authentication middleware (JWT → principal)
3. Permission dependency
4. Workspace header → `ActorContext`
5. Handler resolution
6. Single handler invocation

## Permission codes

Stable codes match `docs/backend/api/API_OVERVIEW.md`:

`assets:read`, `assets:write`, `assets:delete`, `content:read`, `content:write`, `content:delete`, `content:generate`, `publishing:read`, `publishing:write`, `publishing:delete`, `schedule:read`, `schedule:write`, `schedule:delete`, `analytics:read`, `notifications:read`, `notifications:write`, `notifications:delete`, `admin:read`
