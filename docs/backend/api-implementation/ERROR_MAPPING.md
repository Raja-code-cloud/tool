# Error Mapping

Centralized exception handling lives in `api/errors.py` and is registered from `bootstrap/api.py`.

## Failure envelope

All errors return `Content-Type: application/problem+json`:

```json
{
  "success": false,
  "error": {
    "code": "validation_failed",
    "message": "One or more fields failed validation.",
    "details": [{ "field": "title", "code": "missing", "message": "Field required" }]
  },
  "type": "https://api.cloudcontenthub.ai/problems/validation-failed",
  "title": "Unprocessable Content",
  "status": 422,
  "detail": "One or more fields failed validation.",
  "instance": "/api/v1/content/019...",
  "requestId": "req_01"
}
```

The v1 `error` object is authoritative for clients. Optional RFC 9457 top-level fields are additive.

## Application error mapping

| Exception                    | HTTP | Code                       |
| ---------------------------- | ---- | -------------------------- |
| `ValidationError`            | 422  | `validation_failed`        |
| `AuthenticationError`        | 401  | `authentication_required`  |
| `AuthorizationError`         | 403  | `permission_denied`        |
| `ResourceNotFoundError`      | 404  | `resource_not_found`       |
| `ConflictError`              | 409  | `conflict`                 |
| `VersionConflictError`       | 409  | `version_conflict`         |
| `IdempotencyConflictError`   | 409  | `idempotency_conflict`     |
| `StateTransitionError`       | 409  | `invalid_state_transition` |
| `RateLimitError`             | 429  | `rate_limited`             |
| `QuotaExceededError`         | 429  | `quota_exceeded`           |
| `DependencyUnavailableError` | 503  | `dependency_unavailable`   |
| `DependencyTimeoutError`     | 504  | `dependency_timeout`       |
| Unhandled `Exception`        | 500  | `internal_error`           |

## Identity error mapping

Identity infrastructure exceptions are translated before responding:

| Identity exception                             | Application mapping   |
| ---------------------------------------------- | --------------------- |
| `MissingToken`, `InvalidToken`, `TokenExpired` | `AuthenticationError` |
| `PermissionDenied`, `RoleDenied`               | `AuthorizationError`  |

## Request validation

| Source                            | HTTP | Code                |
| --------------------------------- | ---- | ------------------- |
| Malformed JSON body               | 400  | `invalid_request`   |
| FastAPI/Pydantic field validation | 422  | `validation_failed` |

Field violations are copied into `error.details[]` with `field`, `code`, and `message`.

## Feature-specific codes

Application handlers may raise feature exceptions whose codes appear in `docs/backend/api/ERROR_CODES.md` (for example `checksum_mismatch`, `approval_required`, `schedule_time_nonexistent`). These propagate through the generic `ApplicationError` handler using each exception's `code` attribute.

## Logging

- 4xx: warning log with stable `error_code`
- 5xx: error log with stack trace

Logs never include secrets, tokens, or raw provider payloads.

## Handler registration

```python
install_exception_handlers(app)
```

Registers handlers for:

- `ApplicationError`
- `IdentityError`
- `RequestValidationError`
- uncaught `Exception`

Legacy imports from `api/exception_handlers.py` re-export the same functions for backward compatibility.
