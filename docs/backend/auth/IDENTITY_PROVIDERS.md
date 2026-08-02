# Identity Providers

## Supported providers

| Code          | Class                         | Purpose                               |
| ------------- | ----------------------------- | ------------------------------------- |
| `entra`       | `EntraIdentityProvider`       | Microsoft Entra ID (OAuth 2.0 / OIDC) |
| `google`      | `GoogleIdentityProvider`      | Google OAuth 2.0                      |
| `mock`        | `MockIdentityProvider`        | Local development and automated tests |
| `placeholder` | `PlaceholderIdentityProvider` | Future provider extension point       |

## Interface

All providers implement `IdentityProvider`:

- `authenticate()` — begin authorization code + PKCE flow
- `exchange_code()` — validate state/nonce and exchange code
- `refresh()` — rotate application refresh tokens
- `validate_token()` — validate application access tokens
- `get_user()` — resolve user from access token
- `logout()` — revoke refresh session hooks
- `health_check()` — connectivity and JWKS availability
- `supported_scopes()` — advertised OAuth scopes

## Registration

`IdentityFactory.build_registry()` registers enabled providers from `IdentitySettings`:

- `CCH_IDENTITY_MOCK_ENABLED`
- `CCH_IDENTITY_ENTRA_ENABLED`
- `CCH_IDENTITY_GOOGLE_ENABLED`
- `CCH_IDENTITY_PLACEHOLDER_ENABLED`

Production startup rejects mock as the default provider.

## Mock provider

The mock provider requires no external network. Tests obtain a code via `issue_mock_code(subject)` and complete `exchange_code()` using the returned PKCE material from `authenticate()`.

## Adding a provider

1. Create `providers/<name>/provider.py` extending `BaseOAuthProvider` or `IdentityProvider`.
2. Map claims in `claims.py`.
3. Add typed settings to `config.py`.
4. Register in `factory.py`.
5. Document scopes, redirect URIs, and health behavior.

Application modules must not import provider implementations directly.
