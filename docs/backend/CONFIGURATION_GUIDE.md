# Configuration Guide

## Principles

Configuration is typed, immutable after startup, environment supplied, and validated before accepting work. Secrets are values, not files committed to source. The same artifact is promoted through environments; deployment configuration changes behavior at the edges.

Precedence, highest first:

1. explicit test/CLI overrides passed by the composition root;
2. process environment;
3. local development `.env` file;
4. safe code defaults.

Production does not load `.env` files. A variable must have one canonical source after precedence resolution. Startup logs variable names and value sources, never secret values.

## Naming

Use uppercase names with the `CCH_` prefix and explicit units:

```text
CCH_ENVIRONMENT
CCH_SERVICE_NAME
CCH_LOG_LEVEL
CCH_DATABASE_URL
CCH_DATABASE_POOL_SIZE
CCH_DATABASE_TIMEOUT_SECONDS
CCH_OIDC_ISSUER
CCH_OIDC_AUDIENCE
CCH_OIDC_JWKS_CACHE_SECONDS
CCH_AZURE_STORAGE_ACCOUNT_URL
CCH_AZURE_STORAGE_CONTAINER
CCH_QUEUE_NAME
CCH_HTTP_ALLOWED_ORIGINS
CCH_TELEMETRY_ENDPOINT
```

Provider credentials use managed identity/workload identity where available. If a secret reference is necessary, name it by purpose, not vendor payload shape.

## Typed settings

The settings model parses booleans, integers, durations, URLs, origins, and enums strictly. Required values have no production defaults. Unknown `CCH_` variables should fail startup in CI and nonproduction; production rollout may initially warn only during migrations.

Group settings by database, HTTP, auth, storage, queues, providers, telemetry, security, and feature rollout. Domain/application code receives narrow configuration values or ports through dependency injection; it does not read environment variables.

## Secrets

- Store production secrets in an approved cloud secret manager or identity service.
- Never commit `.env`, credentials, private keys, tokens, database passwords, or real endpoint query secrets.
- `.env.example` contains names, descriptions, and non-sensitive placeholders.
- Prefer short-lived credentials and workload identity over static keys.
- Secret access is least-privilege, audited, encrypted in transit/at rest, and separated by environment.
- Rotate without rebuilding the application. Define overlap/reload behavior for each credential.
- Never expose secret values through logs, errors, health endpoints, traces, metrics, configuration dumps, or admin APIs.

OAuth provider tokens stored for product operation use the envelope-encryption design in the database documents; deployment secrets and tenant OAuth material are separate concerns.

## Loading and startup validation

Load settings once in the bootstrap composition root. Validate:

- environment and service identity;
- URLs, allowed schemes, and origin format;
- database TLS and pool bounds;
- issuer/audience and approved JWT algorithms;
- storage container/account and queue names;
- timeout/retry relationships;
- mutually exclusive credential mechanisms;
- production security invariants.

Fail fast with a safe list of invalid variable names and reasons. Do not print values. Readiness remains false until required migrations and dependencies are usable. Optional integrations may start disabled only when explicitly configured and observable.

## Environment policy

`local`, `test`, `staging`, and `production` are recognized deployment classes. Environment checks may select infrastructure defaults but must not bypass authentication, authorization, tenant scope, TLS verification, or redaction. Test-only bypasses live in test composition, never in production branches.

Use feature flags for temporary rollout control. Flags have an owner, purpose, safe default, creation date, expiry/removal issue, and telemetry. Flags do not secure endpoints and cannot replace authorization.

## CORS and lists

Represent allowed origins as a parsed JSON array or documented delimiter format. Exact origins are required in production; wildcard origins are prohibited with credentials. Do not parse comma-separated values ambiguously when values may contain commas.

## Dynamic configuration

Values requiring per-organization/workspace/user/project/social-account inheritance belong in the database `setting_definitions` and `settings` model, not environment variables. Resolution is specific-to-general then definition default, and APIs expose the selected source. Infrastructure settings remain deployment configuration.

## Changes and rotation

Classify each setting as startup-only, safely reloadable, or dynamically resolved. Startup-only changes require rolling deployment. Reloadable changes use an atomic validated snapshot and retain the prior value on failure. Secret rotations include preflight, overlap, cutover, revocation, and verification.

## Documentation and CI

Every setting is documented with type, required environments, safe default, secret classification, reload behavior, and owning component. CI validates `.env.example` against the typed model and scans committed files/history for secrets. Configuration changes receive the same review as code.
