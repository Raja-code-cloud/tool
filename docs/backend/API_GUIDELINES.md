# API Guidelines

## Scope and compatibility

The public backend API is JSON over HTTPS using REST semantics. Base path is `/api/v1`. A major version changes only for intentionally breaking contracts; additive fields and endpoints do not require a new version. Clients must ignore unknown response fields. Never expose database or provider models directly.

## Resource conventions

- Use plural lowercase kebab-case nouns: `/content-assets`, `/social-accounts`.
- Nest only when ownership is required for identity: `/workspaces/{workspaceId}/content-assets`. Avoid more than two resource levels.
- Commands that do not map safely to CRUD use explicit action subresources: `POST /publication-targets/{id}/schedule`, `POST /content-versions/{id}/approve`.
- Do not encode workspace scope only in a client-controlled header. The route contract must make scope explicit for workspace resources.
- Path IDs are UUIDs. Public codes and slugs are used only where documented as stable identifiers.

## HTTP methods and status codes

| Operation        | Method   | Success                                                 |
| ---------------- | -------- | ------------------------------------------------------- |
| List/read        | `GET`    | `200`                                                   |
| Create/command   | `POST`   | `201` with `Location`, or `202` for accepted async work |
| Full replacement | `PUT`    | `200` or `204`; use rarely                              |
| Partial update   | `PATCH`  | `200`                                                   |
| Delete           | `DELETE` | `204`                                                   |

`GET`, `PUT`, and `DELETE` are idempotent. Duplicate-prone `POST` operations require `Idempotency-Key`. The server binds a key to actor, workspace, endpoint, and canonical request hash; reusing it with another payload returns `409`.

## Request and response naming

JSON fields use `camelCase` with explicit mapping to precise `snake_case` database names. Times are RFC 3339 UTC instants. Date-only fields use `YYYY-MM-DD`; IANA time zones are strings. Money is a decimal string plus ISO-4217 currency. Never serialize floating-point money.

Single-resource success:

```json
{ "data": { "id": "019...", "version": 3, "createdAt": "2026-08-02T10:12:00Z" } }
```

Collection success:

```json
{ "data": [], "page": { "nextCursor": null, "hasMore": false }, "meta": { "requestId": "..." } }
```

`meta` is optional except where endpoint metadata is material. Do not wrap `204` responses.

## Pagination

Use opaque cursor pagination for mutable or large collections. Default limit is 25; maximum is 100 unless an endpoint documents a lower cap. Cursor contents are signed/encoded implementation details and include the effective sort key, tie-breaker ID, filter fingerprint, and direction. Invalid or mismatched cursors return `400`.

Offset pagination is allowed only for bounded administrative/catalog data. Responses never include an expensive total count by default; expose totals only when supported by an efficient query.

## Filtering and sorting

- Use repeated query parameters for multi-value filters: `state=scheduled&state=paused`.
- Use explicit range names: `createdAfter`, `createdBefore`.
- Search uses `q`.
- Sort uses `sort=createdAt` or `sort=-createdAt`; support an allowlist only.
- Always add a deterministic ID tie-breaker.
- Unknown filter/sort fields return `400`; they are not silently ignored.
- Filtering, sorting, and pagination are server-side and tenant-scoped.

## Validation

Validate path, query, headers, and body at the delivery boundary, then enforce domain invariants in the application/domain layer. Reject unknown request fields by default for commands. Normalize only harmless formatting; do not silently coerce ambiguous booleans, times, IDs, or enum values.

Scheduling requires `requestedLocalAt`, `timeZone`, and an explicit ambiguity policy/fold when needed. Client validation is never trusted for authorization, MIME type, upload checksum, provider callback, or tenant scope.

## Concurrency

Mutable resources expose integer `version` and an `ETag`. Updates/deletes require `If-Match` or the documented expected version. A stale version returns `409 conflict` with the current version only when disclosure is authorized.

## Errors

All errors use `application/problem+json` based on RFC 9457:

```json
{
  "type": "https://api.cloudcontenthub.ai/problems/version-conflict",
  "title": "Resource version conflict",
  "status": 409,
  "detail": "The resource changed after it was loaded.",
  "code": "version_conflict",
  "instance": "/api/v1/workspaces/.../content-assets/...",
  "requestId": "...",
  "errors": [{ "field": "version", "code": "stale", "message": "Use the latest version." }]
}
```

`detail` is safe and actionable. Stack traces, SQL, provider payloads, token details, and object existence across tenants are prohibited. Validation uses `422`; malformed syntax/query/path uses `400`; unauthenticated `401`; unauthorized `403`; absent or non-disclosable tenant resources `404`; state/idempotency/version conflict `409`; rate limiting `429` with `Retry-After`; unexpected failure `500`.

## Long-running operations

Return `202` with a stable operation/job resource and `Location`. Clients poll that resource or subscribe to an approved event channel. A request timeout does not imply cancellation. Retried commands use the same idempotency key.

## Rate limiting and caching

Rate limits apply by principal, workspace, operation cost, and trusted network attributes. `429` includes `Retry-After`; remaining-quota headers may be exposed if reliable. Authenticated tenant responses default to `Cache-Control: private, no-store`. Catalog/read endpoints may opt into ETag/conditional caching after data classification review.

## OpenAPI conventions

- OpenAPI is generated from explicit transport schemas and checked into CI as a reviewed artifact.
- Every operation has a stable unique `operationId`, summary, tags, authorization requirements, request schema, all material response codes, and examples.
- Reusable problem, pagination, ID, timestamp, money, and version schemas live in components.
- Mark secret/write-only fields `writeOnly`; never include realistic secrets in examples.
- Deprecations are marked in schema and announced with removal date and migration guidance.
- CI rejects undocumented routes, duplicate operation IDs, incompatible schema changes, and public schemas containing ORM/provider objects.
