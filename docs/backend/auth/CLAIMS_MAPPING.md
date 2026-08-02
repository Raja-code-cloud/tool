# Claims Mapping

## Goal

Provider-specific JWT and OIDC claims are normalized into `UnifiedIdentity` before any application code consumes them. Callers never read raw provider payloads.

## Unified fields

| Field                 | Sources (examples)                       |
| --------------------- | ---------------------------------------- |
| `user_id` / `subject` | `sub`, `oid`                             |
| `email`               | `email`, `preferred_username`, `upn`     |
| `display_name`        | `name`, `given_name`                     |
| `tenant_id`           | `tid`, `tenant_id`                       |
| `roles`               | `roles`, `role`, Entra `wids`            |
| `groups`              | `groups`, `group`                        |
| `permissions`         | `permissions` claim when present         |
| `profile_picture`     | `picture`, `avatar_url`                  |
| `provider`            | adapter name (`entra`, `google`, `mock`) |

## Mapping functions

| Provider        | Function                |
| --------------- | ----------------------- |
| Generic OIDC    | `map_standard_claims()` |
| Microsoft Entra | `map_entra_claims()`    |
| Google          | `map_google_claims()`   |
| Mock            | `map_mock_claims()`     |

Conversion helpers:

- `to_unified_identity()` — application identity model
- `to_user_identity()` — provider exchange result model

## Sanitization

Providers implement `sanitize_claims()` to strip sensitive values before diagnostics. Secrets, refresh tokens, and passwords are never exposed.

## Principal attachment

`Principal.from_unified()` stores a redacted claim snapshot (`issuer`, `audience`, `expires_at`, `token_id`) for request context. Full claim payloads are not attached to the principal.
