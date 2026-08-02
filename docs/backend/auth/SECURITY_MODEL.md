# Security Model

## Transport

- HTTPS-only redirect URIs in production (`CCH_IDENTITY_HTTPS_ONLY`)
- Bearer tokens via `Authorization` header
- Secure, HttpOnly, SameSite cookies for browser refresh transport

## OAuth hardening

- PKCE required for Entra, Google, and mock providers
- State and nonce validation on callback
- Exact redirect URI allowlists per provider
- No tokens in redirect URLs

## JWT hardening

- Asymmetric algorithms only
- Issuer allowlist including application issuer and enabled providers
- Audience validation
- Bounded clock skew (`CCH_IDENTITY_CLOCK_SKEW_SECONDS`)
- JWKS fetch timeouts and fail-closed verification

## Authorization

- Authentication failures → `401`
- Authorization failures → `403`
- Infrastructure dependencies fail closed

## Secret handling

- Client secrets and signing keys are settings fields marked `repr=False`
- Structured logging never records tokens, secrets, or raw JWT payloads
- Provider `sanitize_claims()` removes sensitive fields

## CSRF and CORS

- Cookie auth requires CSRF header validation through `CsrfProtector`
- CORS origins configured through `CCH_IDENTITY_CORS_ORIGINS`
- Wildcard origins with credentials are rejected in production

## Extension hooks

| Protocol                 | Purpose                              |
| ------------------------ | ------------------------------------ |
| `CsrfProtector`          | CSRF validation                      |
| `ReplayProtector`        | One-time token consumption           |
| `RevocationStore`        | Refresh/session revocation           |
| `SecretRotationProvider` | Active secret lookup during rotation |
| `AuthorizationHook`      | Custom allow logic                   |
| `AttributePolicy`        | Future ABAC                          |

## Production invariants

Startup validation enforces:

- mock disabled
- HTTPS issuer
- secure cookies
- no wildcard CORS

See `SECURITY_GUIDELINES.md` for platform-wide requirements.
