# Identity Health Checks

## Provider checks

Each `IdentityProvider.health_check()` returns `ProviderHealth`:

| Field            | Meaning                           |
| ---------------- | --------------------------------- |
| `healthy`        | Overall pass/fail                 |
| `provider`       | Provider code                     |
| `detail`         | Safe summary                      |
| `jwks_available` | JWKS endpoint reachable with keys |
| `issuer_valid`   | Issuer configuration present      |

OAuth providers use `JwksHealthChecker` to request the configured JWKS URL with a short timeout.

## Aggregation

`IdentityHealthService.check_all()` executes all registered provider checks and returns `IdentityHealthReport`.

## Readiness integration

Readiness probes should include identity health when external login is required for the deployment. Mock-only local environments may omit provider checks from readiness while still exposing them through diagnostics endpoints wired at the composition root.

## Failure behavior

When JWKS or provider endpoints are unavailable:

- Health reports `healthy=false`
- Login and external token verification fail with `ProviderUnavailable`
- Existing valid application access tokens continue to work until expiry

## Observability

Health checks emit no secrets. Failures should log provider code and safe reason only.

See also `docs/backend/observability/HEALTH_CHECKS.md` for platform-wide health conventions.
