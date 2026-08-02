# Stable Error Codes

Errors follow the failure envelope and RFC 9457 compatibility rules in
[`API_OVERVIEW.md`](API_OVERVIEW.md). Codes and `type` URIs are stable; messages may improve.

| Status | Code                        | Meaning                                                                        |
| -----: | --------------------------- | ------------------------------------------------------------------------------ |
|    400 | `invalid_request`           | Malformed JSON, path, query, header, cursor, sort, or unsupported field.       |
|    401 | `authentication_required`   | No acceptable authentication.                                                  |
|    401 | `invalid_token`             | Token invalid, expired, revoked, wrong issuer/audience, or otherwise unusable. |
|    401 | `invalid_credentials`       | Login credentials rejected without revealing which factor failed.              |
|    401 | `refresh_token_invalid`     | Refresh token missing, expired, revoked, reused, or invalid.                   |
|    403 | `permission_denied`         | Authenticated principal lacks the required permission.                         |
|    403 | `workspace_access_denied`   | Principal cannot act in the selected workspace.                                |
|    404 | `resource_not_found`        | Resource absent, deleted, cross-workspace, or non-disclosable.                 |
|    409 | `version_conflict`          | `If-Match` is stale or missing for a required mutation.                        |
|    409 | `idempotency_conflict`      | Key was reused with a different canonical request.                             |
|    409 | `state_transition_invalid`  | Requested transition is not valid from current state.                          |
|    409 | `resource_conflict`         | A domain uniqueness or active-resource conflict exists.                        |
|    409 | `approval_required`         | Immutable approved content is required before dispatch/scheduling.             |
|    409 | `social_account_unhealthy`  | Target account is disabled, disconnected, or needs reauthorization.            |
|    409 | `schedule_time_ambiguous`   | Local time is ambiguous and no explicit fold/policy resolves it.               |
|    422 | `validation_failed`         | Syntactically valid fields violate bounds, formats, or domain rules.           |
|    422 | `schedule_time_nonexistent` | Local wall time does not exist in the selected IANA zone.                      |
|    413 | `payload_too_large`         | Body/file exceeds endpoint or declared asset limit.                            |
|    415 | `unsupported_media_type`    | Content type, detected file type, or asset-type pairing is unsupported.        |
|    422 | `checksum_mismatch`         | Optional declared SHA-256 differs from observed content.                       |
|    422 | `malware_detected`          | Upload was rejected or quarantined by malware inspection.                      |
|    429 | `rate_limited`              | Request-rate policy exceeded; `Retry-After` is required.                       |
|    429 | `quota_exceeded`            | Plan/workspace byte, AI, publishing, or other quota exceeded.                  |
|    502 | `provider_rejected`         | Provider rejected valid platform work; safe normalized detail only.            |
|    503 | `dependency_unavailable`    | Required database, queue, storage, or provider unavailable.                    |
|    503 | `provider_unavailable`      | External provider temporarily unavailable.                                     |
|    504 | `dependency_timeout`        | Required dependency timed out.                                                 |
|    500 | `internal_error`            | Unexpected server failure; no implementation detail.                           |

Validation `details` use stable field codes including `required`, `invalid_format`, `out_of_range`,
`unknown_field`, `unsupported_value`, `invalid_cursor`, `invalid_sort`, and `content_type_mismatch`.
Cross-workspace guessed IDs always collapse to `resource_not_found`.

Example:

```json
{
  "success": false,
  "error": {
    "code": "schedule_time_ambiguous",
    "message": "The requested local time occurs twice.",
    "details": [{ "field": "fold", "code": "required", "message": "Choose fold 0 or 1." }]
  },
  "type": "https://api.cloudcontenthub.ai/problems/schedule-time-ambiguous",
  "status": 409,
  "requestId": "req_01"
}
```
