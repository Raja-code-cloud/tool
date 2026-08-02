# Common API Schemas

OpenAPI types below are normative JSON shapes. Fields are required unless marked optional. Unknown
request fields are rejected. Database mappings and state authority are in
[`../../../TABLE_SPECIFICATIONS.md`](../../../TABLE_SPECIFICATIONS.md).

## Envelope and primitives

- `Success<T>`: `{success: true, message: string, data: T, meta: Meta}`.
- `PagedResponse<T>`: `Success<T[]>` with `meta.page: Page`.
- `Meta`: `{requestId: string, page?: Page, warnings?: string[]}`.
- `Page`: `{nextCursor: string|null, hasMore: boolean, limit: integer}`.
- `Failure`: `{success: false, error: ApiError}` plus optional compatible RFC 9457 fields.
- `ApiError`: `{code: string, message: string, details: ErrorDetail[]}`.
- `ErrorDetail`: `{field?: string, code: string, message: string}`.
- `Uuid`: UUID string. `Timestamp`: RFC 3339 UTC. `LocalDateTime`: `YYYY-MM-DDTHH:mm:ss` without
  offset. `TimeZone`: IANA name. `Version`: positive integer.
- `ResourceBase`: `{id: Uuid, version: Version, createdAt: Timestamp, updatedAt: Timestamp}`.
- `Operation`: `{id: Uuid, type: "generation"|"publishing"|"upload"|"adminJob",
status: "queued"|"running"|"succeeded"|"failed"|"cancelled", resourceType?: string,
resourceId?: Uuid, createdAt: Timestamp, updatedAt: Timestamp, errorCode?: string}`.

## Identity DTOs

- `User`: `ResourceBase + {email: string|null, displayName: string, avatarUrl?: string|null,
locale: string, timeZone: TimeZone, status: "active"|"disabled"|"anonymized"}`.
- `AuthTokens`: `{accessToken: string, tokenType: "Bearer", expiresIn: integer}`; refresh tokens are
  never returned for browser-cookie transport.
- `Session`: `{user: User, scopes: string[], workspaceIds: Uuid[], access?: AuthTokens}`.
- `AuthProvider`: `{code: string, name: string, authorizationUrl: string, pkceRequired: boolean}`.

## Asset and content DTOs

- `AssetType`: `article|video|poster|thumbnail`.
- `Asset`: `ResourceBase + {assetType: AssetType, title: string, summary: string|null,
lifecycleStatus: "draft"|"active"|"archived", ownerId: Uuid|null, projectId?: Uuid|null,
folderId?: Uuid|null, isFavorite: boolean, media: AssetMedia|null}`.
- `AssetMedia`: `{mimeType: string, byteSize: integer, checksumSha256: string,
scanStatus: "pending"|"clean"|"infected"|"failed", downloadUrl?: string}`. Download URLs are
  short-lived.
- `Content`: `ResourceBase + {assetId: Uuid, title: string, bodyText: string|null,
bodyRich?: object|null, metadata: object, lifecycleStatus: "draft"|"active"|"archived",
origin: "user"|"ai"|"import"|"regeneration", contentVersionId: Uuid|null}`.
- `GenerationRequest`: `{assetId: Uuid, sourceVersionId: Uuid, modelId: Uuid,
promptTemplateId?: Uuid, brandProfileId?: Uuid, scope:
"whole"|"selection"|"headline"|"cta"|"hashtags"|"tone"|"platform_variant",
parameters?: object, selectionText?: string}`.
- `RegenerationRequest`: `GenerationRequest` with required `contentId: Uuid`; `assetId` may be
  omitted because it is resolved tenant-safely from content.

## Publishing and scheduling DTOs

- `PublicationStatus`: `draft|ready|in_progress|completed|partially_failed|cancelled`.
- `Publication`: `ResourceBase + {assetId: Uuid, contentVersionId: Uuid,
approvalRequestId: Uuid|null, title: string, status: PublicationStatus, targets:
PublicationTarget[]}`.
- `PublicationTarget`: `{id: Uuid, socialAccountId: Uuid, platformId: Uuid,
approvalState: "pending"|"approved"|"rejected"|"changes_requested"|"cancelled",
externalPostId?: string|null, externalUrl?: string|null, publishedAt?: Timestamp|null}`.
- `CreatePublicationRequest`: `{contentId: Uuid, contentVersionId: Uuid, title: string,
targets: {socialAccountId: Uuid, generationOutputId?: Uuid}[]}`.
- `ScheduleState`: `draft|scheduled|paused|dispatched|completed|cancelled|failed`.
- `Schedule`: `ResourceBase + {publicationTargetId: Uuid, requestedLocalAt: LocalDateTime,
timeZone: TimeZone, fold: 0|1|null, ambiguityPolicy: "reject"|"earlier"|"later",
scheduledFor: Timestamp, state: ScheduleState, priority: "low"|"normal"|"high"}`.
- `ScheduleRequest`: `{publicationTargetId: Uuid, requestedLocalAt: LocalDateTime,
timeZone: TimeZone, fold?: 0|1, ambiguityPolicy?: "reject"|"earlier"|"later",
priority?: "low"|"normal"|"high"}`. Nonexistent local times fail; ambiguous times require
  `fold` or `earlier|later`.

## Analytics, notification, and operations DTOs

- `MetricValue`: `{code: string, value: string, unit: string, isEstimated: boolean}`; decimal values
  are strings.
- `AnalyticsDashboard`: `{periodStart: Timestamp, periodEnd: Timestamp, timeZone: TimeZone,
freshThrough: Timestamp, methodologyVersion: integer, metrics: MetricValue[]}`.
- `PostPerformance`: `{contentId: Uuid, publicationTargetId?: Uuid, snapshotAt: Timestamp,
reach?: integer, engagements?: integer, clicks?: integer, conversions?: integer,
engagementRate?: string, metrics: MetricValue[]}`.
- `PlatformAnalytics`: `{platformId: Uuid, platformCode: string, accountCount: integer,
metrics: MetricValue[], freshThrough: Timestamp}`.
- `Notification`: `ResourceBase + {typeCode: string, title: string, body: string,
severity: "info"|"success"|"warning"|"error", resourceType?: string|null,
resourceId?: Uuid|null, readAt: Timestamp|null, archivedAt: Timestamp|null,
expiresAt: Timestamp|null}`.
- `Job`: `ResourceBase + {jobType: string, queueName: "ai"|"media"|"notification"|"maintenance",
state: "queued"|"leased"|"running"|"retry_wait"|"succeeded"|"failed"|"dead_lettered"|"cancelled",
resourceType?: string|null, resourceId?: Uuid|null, attemptCount: integer,
maxAttempts: integer, availableAt: Timestamp, completedAt?: Timestamp|null,
errorCode?: string|null}`.
- `QueueSummary`: `{queueName: string, queued: integer, running: integer, retryWait: integer,
failed: integer, deadLettered: integer, oldestQueuedAt: Timestamp|null}`.
- `ProviderStatus`: `{providerType: "ai"|"social"|"storage"|"notification",
code: string, status: "enabled"|"disabled"|"degraded", checkedAt: Timestamp,
message?: string}`.
- `SystemStatus`: `{status: "healthy"|"degraded", version: string, startedAt: Timestamp,
dependencies: {name: string, status: "healthy"|"degraded"|"unavailable"}[]}`.

## Headers and parameters

Reusable headers: `Authorization`, `X-Workspace-ID`, `If-Match`, `Idempotency-Key`,
`X-Request-ID`. Reusable query parameters: `cursor`, `limit`, `q`, `createdAfter`,
`createdBefore`, `updatedAfter`, `updatedBefore`, `occurredAfter`, `occurredBefore`, and `sort`.
Cursor values are opaque and filter-bound. See [`API_OVERVIEW.md`](API_OVERVIEW.md) for limits,
concurrency, replay, and rate headers.

For clients built against the product vocabulary, OpenAPI also declares `page` (integer, minimum 1),
`page_size` (integer, 1–100), `search`, `order` (`asc|desc`), and `filters`. These are compatibility
parameters: `page`/`page_size` are available only on endpoints explicitly marked offset-capable;
`search` aliases `q`; and `order` may be supplied only with an unsigned `sort` value. `filters` is a
JSON-encoded object limited to the endpoint's documented filter allowlist. Clients must not combine
aliases with their canonical equivalents or combine offset pagination with `cursor`; violations
return `400 invalid_request`.

Reusable filter parameters are `createdAfter`, `createdBefore`, `updatedAfter`, `updatedBefore`,
repeated `status`, repeated `platform`, repeated `type`, and repeated `tags`. Feature documents may
use a more precise domain name such as `lifecycleStatus`, `assetType`, or `state`; OpenAPI maps those
fields explicitly rather than treating an unknown generic filter as valid.
