# REST API v1 Overview

This directory defines the public REST contract. Database structure and lifecycle rules remain
authoritative in [`../../../DATABASE_SCHEMA.md`](../../../DATABASE_SCHEMA.md),
[`../../../TABLE_SPECIFICATIONS.md`](../../../TABLE_SPECIFICATIONS.md), and the other root database
documents. General transport rules come from [`../API_GUIDELINES.md`](../API_GUIDELINES.md).
This contract deliberately adapts the requested flat routes to the existing tenant model by requiring
`X-Workspace-ID` on every workspace-scoped operation. New APIs should prefer workspace IDs in paths;
these fixed v1 routes retain the header design.

## Base URLs and route policy

- Business routes: `/api/v1`.
- Canonical health routes: unversioned `/health`, `/ready`, `/live`. If a deployment exposes
  `/api/v1/health` or `/healthz` aliases, they are compatibility aliases only; clients use the
  unversioned canonical routes.
- HTTPS only. JSON fields are `camelCase`; UUIDs are canonical UUID strings; instants are RFC 3339 UTC.
- Unknown request fields and unknown filters/sorts are rejected.

## Public response envelope

All non-`204` v1 successes use the contract-level envelope:

```json
{
  "success": true,
  "message": "Assets retrieved.",
  "data": [],
  "meta": { "requestId": "req_01", "page": { "nextCursor": null, "hasMore": false } }
}
```

`message` is safe human text, not a stable programmatic value. Collections put pagination only under
`meta.page`. This public envelope supersedes the smaller examples in `API_GUIDELINES.md` without
changing the underlying DTOs. A `204` has no body.

Failures use `Content-Type: application/problem+json` and the required v1 shape:

```json
{
  "success": false,
  "error": {
    "code": "validation_failed",
    "message": "Request validation failed.",
    "details": [{ "field": "title", "code": "required", "message": "Title is required." }]
  },
  "type": "https://api.cloudcontenthub.ai/problems/validation-failed",
  "status": 422,
  "requestId": "req_01"
}
```

The optional top-level RFC 9457 fields `type`, `title`, `status`, `detail`, `instance`, and
`requestId` may be added, but never replace or conflict with `error`. See
[`ERROR_CODES.md`](ERROR_CODES.md).

## Authentication, authorization, and workspace

Bearer access tokens use `Authorization: Bearer <token>`. `X-Workspace-ID: <uuid>` is required for
workspace-scoped routes and is validated against active workspace membership before RLS context is
set. It is not trusted by itself. Auth providers and health routes are public. Permissions are stable
codes:

`profile:read`, `profile:write`, `profile:delete`, `assets:read`, `assets:write`,
`assets:delete`, `content:read`, `content:write`, `content:delete`, `content:generate`,
`publishing:read`, `publishing:write`, `publishing:delete`, `schedule:read`, `schedule:write`,
`schedule:delete`, `analytics:read`, `notifications:read`, `notifications:write`,
`notifications:delete`, `admin:read`.

## Shared request rules

- Lists use opaque `cursor`, `limit` (default 25, max 100), `q`, explicit ranges such as
  `createdAfter`, repeated enum filters, and allowlisted `sort`. Leading `-` means descending.
- Default sort is `-updatedAt` for mutable resources and `-occurredAt` for history/event streams,
  always with an ID tie-breaker.
- Mutable resource responses include integer `version` and `ETag: "<version>"`; mutation and
  cancellation endpoints require `If-Match`.
- Duplicate-prone POSTs require `Idempotency-Key`: 8–128 printable non-whitespace token characters.
  Keys bind principal, workspace, operation, and request hash. Results replay for at least 24 hours;
  a changed payload returns `409 idempotency_conflict`.
- `202` responses return an `Operation` DTO and `Location`. Timeout does not imply cancellation.

## Rate-limit contract

| Class         | Contract limit                              |
| ------------- | ------------------------------------------- |
| Login         | 10/minute/IP                                |
| Refresh       | 30/minute/principal                         |
| Read          | 120/minute/principal/workspace              |
| Write         | 60/minute/principal/workspace               |
| AI generation | 10/minute/principal/workspace               |
| Upload        | 20/hour/principal/workspace plus byte quota |
| Publish       | 30/minute/principal/workspace               |
| Analytics     | 60/minute/principal/workspace               |
| Admin         | 60/minute/principal                         |

Deployments may enforce lower plan, abuse, or dependency limits. When reliable,
`X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` are authoritative. Every `429`
includes `Retry-After`; quota exhaustion is also `429 quota_exceeded`.

## Endpoint-document notation

Every endpoint table in this directory is complete. `Common` means the shared rules above and schemas
in [`COMMON_SCHEMAS.md`](COMMON_SCHEMAS.md) apply. `Errors: standard` means the applicable stable
authentication, permission, scope, not-found, validation, conflict, quota/rate, and internal codes in
[`ERROR_CODES.md`](ERROR_CODES.md); endpoint-specific additions are listed. Examples show the
operation-specific payload while retaining the mandatory envelope.

## Health contracts

| Operation      | Contract                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `getHealth`    | **Purpose:** aggregate service health. **Route:** `GET /health`. **Auth/scope:** public. **Headers/params/body:** none. **Response:** `200 Success<Health>` with `status: healthy                                                                                                                                                                                                                                                                                                                          | degraded`; `503 dependency_unavailable`with safe component summaries. **Validation:** none. **Rate:** edge policy, recommended 300/min/IP. **Idempotency:** inherently idempotent. **Example:** request`GET /health`; response `{"success":true,"message":"Service health available.","data":{"status":"healthy","version":"1.0.0"},"meta":{"requestId":"req_01"}}`. |
| `getReadiness` | **Purpose:** report whether required dependencies/migrations can accept traffic. **Route:** `GET /ready`. **Auth/scope:** public. **Headers/params/body:** none. **Response:** `200 Success<Probe>` or `503 dependency_unavailable`; never exposes topology/secrets. **Validation:** none. **Rate:** edge policy, recommended 300/min/IP. **Idempotency:** inherent. **Example:** `GET /ready` → `{"success":true,"message":"Service is ready.","data":{"status":"ready"},"meta":{"requestId":"req_02"}}`. |
| `getLiveness`  | **Purpose:** prove the process can run, not dependency health. **Route:** `GET /live`. **Auth/scope:** public. **Headers/params/body:** none. **Response:** `200 Success<Probe>`; `500 internal_error` only when process-level checks fail. **Validation:** none. **Rate:** edge policy, recommended 300/min/IP. **Idempotency:** inherent. **Example:** `GET /live` → `{"success":true,"message":"Service is live.","data":{"status":"live"},"meta":{"requestId":"req_03"}}`.                             |

## Document map

Auth, user, asset, content, publishing, scheduling, analytics, notification, and admin contracts are
split by feature. [`OPENAPI_STRUCTURE.md`](OPENAPI_STRUCTURE.md) is the complete OpenAPI 3.1
operation registry and component blueprint.
