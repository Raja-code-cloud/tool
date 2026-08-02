# Error Handling

## Principles

Errors are stable application contracts. Domain/application layers raise typed exceptions; delivery and worker boundaries translate them. Internal details are logged securely and never returned to clients. A resource outside the caller's tenant or disclosure rights is treated as not found.

## Exception hierarchy

```text
ApplicationError
├── ClientError
│   ├── ValidationError
│   ├── AuthenticationError
│   ├── AuthorizationError
│   ├── ResourceNotFoundError
│   ├── ConflictError
│   │   ├── VersionConflictError
│   │   ├── IdempotencyConflictError
│   │   └── StateTransitionError
│   ├── RateLimitError
│   └── QuotaExceededError
├── DependencyError
│   ├── DependencyUnavailableError
│   ├── DependencyTimeoutError
│   ├── ProviderAuthenticationError
│   └── ProviderRateLimitError
└── InternalError
```

Feature-specific business exceptions derive from the closest stable base: `ApprovalRequiredError`, `ScheduleTimeAmbiguousError`, `ScheduleTimeNonexistentError`, `SocialAccountUnhealthyError`, and similar names. Each exception carries a machine code, safe message parameters, and optional structured field violations. It does not carry an HTTP response or raw provider payload.

## Validation

Transport validation covers malformed JSON, field types, bounds, formats, and unknown fields. It returns one or more field violations. Domain validation covers current state and cross-record invariants. Do not leak schema/library-specific error objects; normalize paths and stable error codes.

Use `400` for malformed syntax/query/path and `422` for a syntactically valid request whose fields fail validation. Invalid tenant scope is never defaulted.

## HTTP mapping

| Exception/category                 |     Status | Stable code                                 |
| ---------------------------------- | ---------: | ------------------------------------------- |
| Authentication                     |        401 | `authentication_required` / `invalid_token` |
| Authorization                      |        403 | `permission_denied`                         |
| Missing/non-disclosable resource   |        404 | `resource_not_found`                        |
| Validation                         |    400/422 | `invalid_request` / `validation_failed`     |
| Version/state/idempotency conflict |        409 | specific conflict code                      |
| Quota exceeded                     | 403 or 429 | `quota_exceeded`                            |
| Rate limited                       |        429 | `rate_limited`                              |
| Dependency unavailable/timeout     |    503/504 | `dependency_unavailable`                    |
| Unexpected error                   |        500 | `internal_error`                            |

Responses use the RFC 9457 problem format defined in `API_GUIDELINES.md`. `type`, `code`, and field error codes are stable; safe human text may evolve. Include `requestId`, never a stack trace.

## Database and concurrency translation

Translate expected database outcomes at the repository boundary:

- zero-row optimistic update -> `VersionConflictError`;
- known active-row unique constraint -> domain-specific conflict;
- tenant-safe FK failure -> validation/conflict or internal invariant breach based on cause;
- serialization/deadlock -> bounded retry only when the entire transaction is safe and idempotent;
- unavailable connection -> dependency unavailable.

Do not parse arbitrary database message text. Map named constraints explicitly. Unexpected integrity errors remain internal and trigger operational alerts.

## External providers

Adapters normalize failures into retryable timeout/unavailable, rate limited with retry time, authentication/reauthorization required, invalid provider request, rejected content, and terminal failure. Store only redacted diagnostics and provider request IDs. Provider wording and status codes do not leak into public contracts.

## Worker handling

Job boundaries classify errors as:

- **retryable:** transient network, provider 5xx, lock contention; backoff with jitter;
- **scheduled retry:** provider rate limit; honor a safe `Retry-After`;
- **non-retryable:** invalid state, revoked account, unsupported capability;
- **poison/unknown:** bounded attempts, then dead-letter and alert.

Handlers update job/attempt state and release or expire leases atomically where possible. At-least-once delivery means a retry may follow a successful side effect; idempotency is mandatory.

## Logging and reporting

Expected client errors are logged at `info` or `warning` without stack traces. Unexpected failures are logged once at the outer boundary with exception details, request/correlation IDs, actor/workspace identifiers when permitted, and redacted operation metadata. Do not log the same exception at every layer.

## Operational behavior

Never catch and continue after invariant corruption, cancellation, or process-fatal conditions. Graceful shutdown propagates cancellation and rolls back open units of work. Error handling itself must not hide the original error if audit, metrics, or logging fails; secondary failures are reported separately.
