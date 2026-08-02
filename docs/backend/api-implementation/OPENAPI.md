# OpenAPI Integration

OpenAPI 3.1 customization is implemented in `api/openapi.py` and applied from `bootstrap/api.py` via `configure_openapi()`.

## Document metadata

- OpenAPI version: `3.1.0`
- Title: Cloud Content Hub AI REST API
- Default security: `bearerAuth` (JWT)
- Service metadata extension: `info.x-service-name`

## Tags

Primary tags registered for all routers:

- Health, Assets, Content, Publishing, Scheduler, Analytics, Notifications, Admin

Each route function sets a single primary tag and a unique `operation_id` matching `docs/backend/api/OPENAPI_STRUCTURE.md`.

## Security schemes

```yaml
bearerAuth:
  type: http
  scheme: bearer
  bearerFormat: JWT
```

Health routes use no security requirement. Workspace-scoped routes declare the `X-Workspace-ID` header parameter in router signatures.

## Reusable components

`openapi.py` registers:

- Schemas: `Failure`, `ApiError`, `ErrorDetail`, `Meta`, `Page`, `Health`, `Probe`
- Responses: `BadRequest`, `Unauthenticated`, `Forbidden`, `NotFound`, `Conflict`, `Unprocessable`, `RateLimited`, `Unavailable`, `InternalError`

All failure responses reference `application/problem+json`.

## Response headers

Routers emit contract headers where required:

| Header             | When                                        |
| ------------------ | ------------------------------------------- |
| `ETag`             | Versioned resource GET/PATCH/POST responses |
| `Location`         | `201`/`202` creation and async acceptance   |
| `X-Request-ID`     | All responses (request context middleware)  |
| `X-Correlation-ID` | All responses (request context middleware)  |

## Examples

Router docstrings and `responses={}` declarations on mutating routes document success status codes (`201`, `202`, `204`). Full JSON examples remain authoritative in the feature API documents under `docs/backend/api/`.

## Swagger UI

When `Settings.openapi_enabled` is true:

- `/openapi.json` — generated schema
- `/docs` — Swagger UI with request duration display and authorization persistence

## Client generation rules

Generated clients must preserve:

- v1 success envelope (`success`, `message`, `data`, `meta.page`)
- RFC 9457 failure envelope (`success: false`, `error`, optional `type`/`status`/`requestId`)
- camelCase field names
- Stable `operationId` values for MSW and SDK generation
