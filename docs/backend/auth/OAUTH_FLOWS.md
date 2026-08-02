# OAuth Flows

## Authorization code + PKCE

All external providers use the authorization code flow with PKCE (`S256`).

1. Client calls provider `authenticate(redirect_uri)`.
2. Infrastructure generates `state`, `nonce`, and PKCE verifier/challenge.
3. Client redirects the user to the returned authorization URL.
4. Provider redirects back with `code` and `state`.
5. Client calls `exchange_code()` with the original PKCE verifier and expected state/nonce.
6. Infrastructure exchanges the code, validates the ID token, and issues application tokens.

## Validations

| Check                    | Module                                     |
| ------------------------ | ------------------------------------------ |
| Redirect URI allowlist   | `validators.validate_redirect_uri()`       |
| State equality           | `validators.validate_state()`              |
| Nonce in ID token        | `validators.validate_nonce()`              |
| PKCE verifier format     | `validators.validate_code_verifier()`      |
| Authorization code shape | `validators.validate_authorization_code()` |

## Provider endpoints

### Microsoft Entra ID

- Authorize: `{authority}/oauth2/v2.0/authorize`
- Token: `{authority}/oauth2/v2.0/token`
- JWKS: `{authority}/discovery/v2.0/keys`

### Google

- Authorize: `https://accounts.google.com/o/oauth2/v2/auth`
- Token: `https://oauth2.googleapis.com/token`
- JWKS: `https://www.googleapis.com/oauth2/v3/certs`

## Refresh and logout

- Application refresh tokens rotate through `TokenService.refresh_access_token()`.
- Logout revokes refresh sessions through `RevocationStore` when configured.
- Provider logout URLs may be returned for federated sign-out; application session revocation remains authoritative.

## CSRF

Cookie-based refresh and logout require the CSRF header configured as `CCH_IDENTITY_CSRF_HEADER`. Bearer-only clients are not cookie authenticated and therefore do not use CSRF cookies.
