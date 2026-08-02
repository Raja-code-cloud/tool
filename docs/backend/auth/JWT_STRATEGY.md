# JWT Strategy

## Token types

| Type        | Purpose              | Lifetime                                         |
| ----------- | -------------------- | ------------------------------------------------ |
| Access      | API authorization    | `CCH_IDENTITY_ACCESS_TOKEN_MINUTES` (default 15) |
| Refresh     | Session rotation     | `CCH_IDENTITY_REFRESH_TOKEN_DAYS` (default 30)   |
| External ID | Provider login proof | Provider controlled                              |

## Signing

Application tokens are signed with an RSA key configured through `CCH_IDENTITY_SIGNING_KEY_PEM`. When no key is supplied in non-production environments, the factory generates an ephemeral RSA pair.

Allowed algorithms are configured through `CCH_IDENTITY_ALLOWED_ALGORITHMS` (default `RS256`, `ES256`). Symmetric and `none` algorithms are rejected at startup.

## Verification

`JwtService.decode_and_verify()` enforces:

- signature validation
- issuer allowlist (`effective_allowed_issuers`)
- audience match
- expiry and not-before with configurable clock skew
- required claims (`sub`, `iss`, `aud`, `exp`)
- expected token type (`access` / `refresh`)

External provider tokens are verified against provider JWKS URLs with the same constraints.

## JWKS caching

JWKS clients are cached per URL for `CCH_IDENTITY_JWKS_CACHE_SECONDS`. Cache refresh occurs on expiry or unknown key ID. Verification fails closed when JWKS is unavailable.

## Security rules

- Never log token contents, secrets, or authorization headers.
- Refresh tokens are revocable through `RevocationStore`.
- Browser refresh transport uses secure cookie settings from `CookieSettings`.

## Testing

Unit tests use generated RSA keys through `identity_factory()` and never call external issuers.
