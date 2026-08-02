# OpenAPI 3.1 Structural Blueprint

This is the normative assembly blueprint for a generated OpenAPI document. It is intentionally not a
duplicate giant YAML file. Combined with endpoint documents and schemas, it contains every path,
unique operation ID, request/response reference, and material status needed to generate frontend
types and mocks.

## Root document

```yaml
openapi: 3.1.0
info:
  title: Cloud Content Hub AI REST API
  version: 1.0.0
  description: Public v1 contract; success envelopes and RFC 9457-compatible failures.
servers:
  - url: https://api.cloudcontenthub.ai/api/v1
    description: Production business API
  - url: /api/v1
    description: Same-origin business API
security:
  - bearerAuth: []
```

Health paths are absolute unversioned paths represented in the assembled artifact with a separate
server `{url: https://api.cloudcontenthub.ai}` or with path-item server overrides. Do not concatenate
`/api/v1` onto `/health`, `/ready`, or `/live`.

## Tags

`Health` (runtime probes), `Auth` (sessions/providers), `Users` (global profile), `Assets` (private
storage/library), `Content` (drafts/versions/AI), `Publishing` (publication dispatch/history),
`Scheduler` (wall-time schedules), `Analytics` (normalized metrics), `Notifications` (recipient
inbox), and `Admin` (safe operational summaries). Each operation has exactly one primary tag.

## Security schemes and reusable parameters

- `bearerAuth`: HTTP `bearer`, format `JWT`.
- `refreshCookie`: API key in cookie, name deployment-defined and documented as `cch_refresh`;
  used only by refresh/logout. A registered confidential-client body token is an alternative.
- `WorkspaceId`: header `X-Workspace-ID`, required UUID on workspace-scoped operations.
- `IfMatch`: required header string ETag on mutable operations.
- `IdempotencyKey`: required header string, pattern printable non-whitespace token, min 8, max 128.
- `Cursor`, `Limit` (default 25, max 100), `Q`, range and `Sort` parameters follow
  [`COMMON_SCHEMAS.md`](COMMON_SCHEMAS.md). Repeated filters use `style: form`, `explode: true`.
- Compatibility parameters `page`, `page_size`, `search`, `order`, and JSON-object `filters` follow
  the mutual-exclusion and endpoint allowlist rules in `COMMON_SCHEMAS.md`; offset parameters are
  emitted only for operations explicitly designated offset-capable.

Auth providers and health use `security: []`. Login uses `security: []`; refresh declares
`refreshCookie` or registered token transport. Global user/auth routes do not declare `WorkspaceId`.

## Component schemas

The artifact defines `$defs`-compatible OpenAPI schemas for every named DTO in
[`COMMON_SCHEMAS.md`](COMMON_SCHEMAS.md): `Success`, `PagedResponse`, `Meta`, `Page`, `Failure`,
`ApiError`, `ErrorDetail`, `ResourceBase`, `Operation`, `User`, `AuthTokens`, `Session`,
`AuthProvider`, `Asset`, `AssetMedia`, `Content`, `GenerationRequest`, `RegenerationRequest`,
`Publication`, `PublicationTarget`, `CreatePublicationRequest`, `Schedule`, `ScheduleRequest`,
`MetricValue`, `AnalyticsDashboard`, `PostPerformance`, `PlatformAnalytics`, `Notification`, `Job`,
`QueueSummary`, `ProviderStatus`, and `SystemStatus`.

Add operation-only schemas: `LoginRequest`, `UpdateUserRequest`, `UploadAssetRequest`,
`ReplaceAssetRequest`, `UpdateContentRequest`, `DuplicateContentRequest`,
`DispatchPublicationRequest`, `UpdateScheduleRequest`, `MarkNotificationReadRequest`,
`PublicationHistoryItem`, `Health`, and `Probe`. Generic success/paged schemas are specialized using
`allOf` and concrete `data` properties so generators produce useful types. Every object sets
`additionalProperties: false` except explicitly open metadata/provider parameter objects, which have
size/depth constraints.

## Reusable responses

Define component responses `BadRequest` (400), `Unauthenticated` (401), `Forbidden` (403),
`NotFound` (404), `Conflict` (409), `PayloadTooLarge` (413), `UnsupportedMediaType` (415),
`Unprocessable` (422), `RateLimited` (429 with `Retry-After`), `ProviderFailure` (502),
`Unavailable` (503), `Timeout` (504), and `InternalError` (500). Each uses
`application/problem+json` and `Failure`. Success components include standard `X-Request-ID`,
rate headers, optional `ETag`, and `Location` where specified. `NoContent` has no content.

## Complete operation registry

`Req` names a request schema or `—`; `OK` lists success status/schema; `Errors` lists material status
responses in addition to the shared 500 response. All business paths below are relative to
`/api/v1`; health paths are unversioned.

| Tag           | Method and path                  | operationId              | Security / permission                        | Req                             | OK                                          | Errors                                    |
| ------------- | -------------------------------- | ------------------------ | -------------------------------------------- | ------------------------------- | ------------------------------------------- | ----------------------------------------- |
| Health        | `GET /health`                    | `getHealth`              | public                                       | —                               | `200 Success<Health>`                       | `503`                                     |
| Health        | `GET /ready`                     | `getReadiness`           | public                                       | —                               | `200 Success<Probe>`                        | `503`                                     |
| Health        | `GET /live`                      | `getLiveness`            | public                                       | —                               | `200 Success<Probe>`                        | `500`                                     |
| Auth          | `POST /auth/login`               | `login`                  | public                                       | `LoginRequest`                  | `200 Success<Session>`                      | `400,401,429,503`                         |
| Auth          | `POST /auth/logout`              | `logout`                 | bearer/refresh                               | —                               | `204`                                       | `400,401,429`                             |
| Auth          | `POST /auth/refresh`             | `refreshAccessToken`     | refresh                                      | refresh token alternative       | `200 Success<AuthTokens>`                   | `400,401,429,503`                         |
| Auth          | `GET /auth/me`                   | `getCurrentSession`      | bearer                                       | —                               | `200 Success<Session>`                      | `401,429`                                 |
| Auth          | `GET /auth/providers`            | `listAuthProviders`      | public                                       | —                               | `200 Success<AuthProvider[]>`, `304`        | `429,503`                                 |
| Users         | `GET /users/me`                  | `getUserProfile`         | `profile:read`                               | —                               | `200 Success<User>`, `304`                  | `401,403,429`                             |
| Users         | `PATCH /users/me`                | `updateUserProfile`      | `profile:write`, If-Match                    | `UpdateUserRequest`             | `200 Success<User>`                         | `400,401,403,409,422,429`                 |
| Users         | `DELETE /users/me`               | `deleteUserProfile`      | `profile:delete`, If-Match                   | —                               | `202 Success<Operation>`                    | `401,403,409,429`                         |
| Assets        | `POST /assets/upload`            | `uploadAsset`            | workspace, `assets:write`, key               | `UploadAssetRequest` multipart  | `202 Success<Operation>`                    | `400,401,403,409,413,415,422,429,503`     |
| Assets        | `GET /assets`                    | `listAssets`             | workspace, `assets:read`                     | —                               | `200 PagedResponse<Asset>`                  | `400,401,403,429`                         |
| Assets        | `GET /assets/search`             | `searchAssets`           | workspace, `assets:read`                     | —                               | `200 PagedResponse<Asset>`                  | `400,401,403,429`                         |
| Assets        | `GET /assets/{id}`               | `getAsset`               | workspace, `assets:read`                     | —                               | `200 Success<Asset>`, `304`                 | `400,401,403,404,429`                     |
| Assets        | `DELETE /assets/{id}`            | `deleteAsset`            | workspace, `assets:delete`, If-Match         | —                               | `204`                                       | `400,401,403,404,409,429`                 |
| Assets        | `POST /assets/{id}/replace`      | `replaceAssetFile`       | workspace, `assets:write`, If-Match, key     | `ReplaceAssetRequest` multipart | `202 Success<Operation>`                    | `400,401,403,404,409,413,415,422,429,503` |
| Content       | `POST /content/generate`         | `generateContent`        | workspace, `content:generate`, key           | `GenerationRequest`             | `202 Success<Operation>`                    | `400,401,403,404,409,422,429,503`         |
| Content       | `POST /content/regenerate`       | `regenerateContent`      | workspace, `content:generate`, key           | `RegenerationRequest`           | `202 Success<Operation>`                    | `400,401,403,404,409,422,429,503`         |
| Content       | `GET /content`                   | `listContent`            | workspace, `content:read`                    | —                               | `200 PagedResponse<Content>`                | `400,401,403,429`                         |
| Content       | `GET /content/{id}`              | `getContent`             | workspace, `content:read`                    | —                               | `200 Success<Content>`, `304`               | `400,401,403,404,429`                     |
| Content       | `PATCH /content/{id}`            | `updateContent`          | workspace, `content:write`, If-Match         | `UpdateContentRequest`          | `200 Success<Content>`                      | `400,401,403,404,409,422,429`             |
| Content       | `DELETE /content/{id}`           | `deleteContent`          | workspace, `content:delete`, If-Match        | —                               | `204`                                       | `400,401,403,404,409,429`                 |
| Content       | `POST /content/{id}/duplicate`   | `duplicateContent`       | workspace, `content:write`, key              | `DuplicateContentRequest`       | `201 Success<Content>`                      | `400,401,403,404,409,422,429`             |
| Content       | `POST /content/{id}/archive`     | `archiveContent`         | workspace, `content:write`, If-Match         | —                               | `200 Success<Content>`                      | `400,401,403,404,409,429`                 |
| Publishing    | `POST /publish`                  | `createPublication`      | workspace, `publishing:write`, key           | `CreatePublicationRequest`      | `201 Success<Publication>`                  | `400,401,403,404,409,422,429`             |
| Publishing    | `POST /publish/{id}`             | `dispatchPublication`    | workspace, `publishing:write`, If-Match, key | `DispatchPublicationRequest`    | `202 Success<Operation>`                    | `400,401,403,404,409,422,429,502,503`     |
| Publishing    | `GET /publish/history`           | `listPublicationHistory` | workspace, `publishing:read`                 | —                               | `200 PagedResponse<PublicationHistoryItem>` | `400,401,403,429`                         |
| Publishing    | `DELETE /publish/{id}`           | `cancelPublication`      | workspace, `publishing:delete`, If-Match     | —                               | `200 Success<Publication>`                  | `400,401,403,404,409,429`                 |
| Scheduler     | `POST /schedule`                 | `createSchedule`         | workspace, `schedule:write`, key             | `ScheduleRequest`               | `201 Success<Schedule>`                     | `400,401,403,404,409,422,429`             |
| Scheduler     | `GET /schedule`                  | `listSchedules`          | workspace, `schedule:read`                   | —                               | `200 PagedResponse<Schedule>`               | `400,401,403,429`                         |
| Scheduler     | `GET /schedule/{id}`             | `getSchedule`            | workspace, `schedule:read`                   | —                               | `200 Success<Schedule>`, `304`              | `400,401,403,404,429`                     |
| Scheduler     | `PATCH /schedule/{id}`           | `updateSchedule`         | workspace, `schedule:write`, If-Match        | `UpdateScheduleRequest`         | `200 Success<Schedule>`                     | `400,401,403,404,409,422,429`             |
| Scheduler     | `DELETE /schedule/{id}`          | `cancelSchedule`         | workspace, `schedule:delete`, If-Match       | —                               | `200 Success<Schedule>`                     | `400,401,403,404,409,429`                 |
| Analytics     | `GET /analytics/dashboard`       | `getAnalyticsDashboard`  | workspace, `analytics:read`                  | —                               | `200 Success<AnalyticsDashboard>`           | `400,401,403,422,429,503`                 |
| Analytics     | `GET /analytics/posts`           | `listAnalyticsPosts`     | workspace, `analytics:read`                  | —                               | `200 PagedResponse<PostPerformance>`        | `400,401,403,422,429`                     |
| Analytics     | `GET /analytics/platforms`       | `listAnalyticsPlatforms` | workspace, `analytics:read`                  | —                               | `200 Success<PlatformAnalytics[]>`          | `400,401,403,422,429`                     |
| Analytics     | `GET /analytics/post/{id}`       | `getAnalyticsPost`       | workspace, `analytics:read`                  | —                               | `200 Success<PostPerformance>`, `304`       | `400,401,403,404,422,429`                 |
| Notifications | `GET /notifications`             | `listNotifications`      | workspace, `notifications:read`              | —                               | `200 PagedResponse<Notification>`           | `400,401,403,429`                         |
| Notifications | `PATCH /notifications/{id}/read` | `markNotificationRead`   | workspace, `notifications:write`, If-Match   | `MarkNotificationReadRequest`   | `200 Success<Notification>`                 | `400,401,403,404,409,422,429`             |
| Notifications | `DELETE /notifications/{id}`     | `deleteNotification`     | workspace, `notifications:delete`, If-Match  | —                               | `204`                                       | `400,401,403,404,409,429`                 |
| Admin         | `GET /admin/jobs`                | `listAdminJobs`          | `admin:read`                                 | —                               | `200 PagedResponse<Job>`                    | `400,401,403,429`                         |
| Admin         | `GET /admin/queues`              | `listAdminQueues`        | `admin:read`                                 | —                               | `200 Success<QueueSummary[]>`               | `400,401,403,429,503`                     |
| Admin         | `GET /admin/providers`           | `listAdminProviders`     | `admin:read`                                 | —                               | `200 Success<ProviderStatus[]>`             | `400,401,403,429`                         |
| Admin         | `GET /admin/system`              | `getAdminSystemStatus`   | `admin:read`                                 | —                               | `200 Success<SystemStatus>`                 | `401,403,429,503`                         |

## Path assembly and mock-generation rules

Path parameters use reusable `UuidPathId` and are always required. Declare specific static paths such
as `/assets/search` and `/publish/history` alongside parameter paths without routing ambiguity.
Every response includes a concrete example from its feature document. Generated mocks must preserve
envelopes, `meta.page`, ETags/version increments, `Location` for 201/202, empty 204 bodies, stable
errors, workspace isolation, and async operation progression. CI must reject duplicate operation IDs,
missing material responses, undocumented routes, schemas exposing persistence/provider objects, or
non-camelCase public properties.
