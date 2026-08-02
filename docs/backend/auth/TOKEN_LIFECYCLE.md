# Token Lifecycle

## Issuance

After successful provider authentication:

1. External ID token claims map to `UnifiedIdentity`.
2. `TokenService.issue_session()` creates:
   - access JWT (`token_type=access`)
   - refresh JWT (`token_type=refresh`, includes `jti`)
3. Token lifetimes come from `IdentitySettings`.

## API usage

Clients send access tokens using `Authorization: Bearer <token>`. `AuthenticationMiddleware` validates the token and binds a `Principal` to the request context.

## Refresh

`POST /api/v1/auth/refresh` (application layer) should call `TokenService.refresh_access_token()`:

- Validates refresh token type and signature
- Checks revocation through `RevocationStore`
- Issues a new access token
- Rotates refresh token when session persistence is added at the application layer

## Revocation

`RevocationStore` provides:

- `is_revoked(token_id)`
- `revoke(token_id, expires_at)`

Infrastructure includes `InMemoryRevocationStore` for tests. Production should use a durable store wired at the composition root.

## Expiry handling

Expired tokens raise `TokenExpired`. Middleware treats invalid tokens as anonymous unless a route dependency requires authentication.

## Replay protection

`ReplayProtector` and `RevocationStore` protocols provide hooks for replay detection. Application session persistence completes the rotation and reuse detection described in `AUTH_API.md`.
