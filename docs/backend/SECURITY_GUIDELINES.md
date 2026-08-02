# Security Guidelines

## Security model

Apply zero trust, least privilege, defense in depth, secure defaults, and fail-closed behavior. Workspace is the authorization boundary; organization is the commercial boundary. RLS and tenant-safe foreign keys reinforce application authorization but do not replace it.

## JWT and sessions

- Accept tokens only over TLS and normally through the `Authorization: Bearer` header.
- Validate signature against trusted issuer metadata, exact issuer and audience, approved asymmetric algorithm, expiry, not-before, and key ID.
- Never accept `none`, algorithm substitution, token-provided JWK URLs, or unbounded clock skew.
- Cache JWKS with bounded TTL and safe refresh on unknown keys; fail closed when verification is impossible.
- Resolve `(issuer, subject)` to one active external identity. Do not key users by email.
- Enforce user/session revocation where applicable. Store only hashed refresh-session metadata, never bearer tokens.
- Browser refresh tokens use `Secure`, `HttpOnly`, appropriate `SameSite`, narrow path/domain, rotation, reuse detection, and CSRF protection where cookie authentication is used.

Authentication errors are `401`; authenticated but unauthorized requests are `403`; tenant resources whose existence is not disclosable return `404`.

## Password hashing

If local passwords are introduced, use Argon2id through an approved maintained library with parameters benchmarked for the deployment and recorded in the hash. Use a unique random salt and optional managed pepper. Compare in constant time, rehash after successful login when parameters change, rate-limit login/recovery, and never log passwords. Do not invent password cryptography. Prefer OIDC and phishing-resistant MFA.

## RBAC and tenant authorization

Permissions are stable catalog codes assigned through workspace roles and active memberships. Organization membership does not imply workspace access. Application use cases check the required permission and relevant resource relationship on every command/query. UI visibility is not enforcement.

Every workspace repository method requires validated `workspace_id`; every transaction sets transaction-local RLS context after authorization. Background global claimers use separate minimal roles and re-establish tenant context before loading business aggregates. Privileged maintenance access is separate, time-bound, approved, and audited.

## Input validation

Validate all request parts, message/event payloads, provider callbacks, files, and external responses with strict schemas, size/depth/count limits, and allowlists. Parameterize SQL. Encode output for its sink. Normalize Unicode/filenames carefully and preserve original safe display metadata separately.

Uploads use backend-issued short-lived capabilities with object/key, size, MIME, checksum, and operation restrictions. Finalization verifies server-observed metadata and malware scanning before content becomes usable. Never trust filename extension or client MIME.

Protect outbound HTTP against SSRF: allowlist schemes/hosts where possible, resolve and reject private/link-local/metadata ranges, limit redirects, pin timeouts and response sizes, and revalidate redirect targets.

## CORS and CSRF

Production CORS uses exact HTTPS origin allowlists, minimal methods/headers, and only enables credentials when required. Wildcard origin with credentials is prohibited. CORS is not authorization. Cookie-authenticated state changes require CSRF tokens and Origin/Referer validation; bearer tokens outside cookies reduce but do not eliminate browser threat review.

## Security headers

At the trusted edge/API return, as applicable:

- `Strict-Transport-Security` after all subdomains are HTTPS-ready;
- `X-Content-Type-Options: nosniff`;
- `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'` for JSON/API responses;
- `X-Frame-Options: DENY` for legacy defense;
- `Referrer-Policy: no-referrer`;
- a restrictive `Permissions-Policy`;
- `Cache-Control: no-store` for authenticated/sensitive responses.

Remove unnecessary server/version headers. Enforce TLS 1.2+ and certificate verification.

## Secrets and encryption

Use managed identity and an approved secret manager. Separate credentials by service, environment, and privilege. Rotate and audit access. OAuth tokens are envelope-encrypted ciphertext or managed-secret references with key version; plaintext is prohibited in database, logs, events, traces, or errors. Signed URLs are short-lived and least-privilege.

Use platform-managed encryption at rest and TLS in transit. Application-level encryption keys reside outside the database. Define key rotation and cryptographic erasure. Passwords are hashed, not encrypted.

## Integrations and webhooks

OAuth uses state and PKCE where supported, exact redirect URIs, minimal scopes, and account/workspace binding before persistence. Webhooks verify provider signature over raw bytes, timestamp tolerance, expected source where reliable, and replay/dedupe before processing. Record redacted receipts and acknowledge only according to provider retry semantics.

## Abuse prevention

Apply request body limits, timeouts, concurrency controls, per-principal/workspace rate limits, quotas, and cost controls for AI, upload, export, analytics, and publishing operations. Idempotency keys prevent duplicate side effects but do not replace rate limits. Enumeration-sensitive flows use consistent responses and timing where practical.

## Logging, audit, and privacy

Follow `LOGGING_GUIDELINES.md`. Material authorization, role, OAuth, publishing, export, deletion, billing, and break-glass actions create append-only audit records with redacted safe diffs. Apply data minimization, retention, legal hold, export, and erasure policies from the database design.

## Supply chain and operations

Pin dependencies with hashes/lockfiles, scan dependencies and images, generate an SBOM, verify build provenance where available, run as non-root with a read-only filesystem where practical, and keep request, worker, migration, and maintenance credentials separate. Patch critical vulnerabilities under the security response SLA.

Readiness must not expose secrets or internal topology. Administrative/debug endpoints are disabled publicly and strongly authenticated. Security findings have an owner, severity, remediation date, and regression test.

## Mandatory tests

CI and pre-release tests cover broken access control, cross-tenant guessed IDs and joins, JWT confusion, revoked sessions, privilege changes, injection, SSRF, malicious uploads, CORS/CSRF, webhook replay, idempotency abuse, sensitive-data leakage, and ordinary-role attempts to bypass immutable/RLS protections.
