# Hardening Checklist

Review date: 2026-08-02  
Use before production deployment and after each security-relevant change.

## Risk Register

| ID | Title | Severity | Status | Owner |
|----|-------|----------|--------|-------|
| R-001 | Missing HTTP security headers | High | Open | platform-security |
| R-002 | No HTTP rate limiting | High | Open | platform-security |
| R-003 | Workspace membership not enforced | High | Open | platform-security |
| R-004 | Worker wildcard permissions | Medium | Accepted | platform-security |
| R-005 | No RLS in migrations | Medium | Open | platform-security |
| R-006 | No-op virus scan default | Medium | Open | platform-security |
| R-007 | RevocationStore not wired | Medium | Open | platform-security |
| R-008 | No SSRF protection | Medium | Open | platform-security |
| R-009 | CSRF protocol only | Low | Open | platform-security |
| R-010 | No dependency lockfile | Low | Open | platform-security |

## Authentication & Identity

- [x] JWT uses asymmetric algorithms only (RS256/ES256)
- [x] Production rejects mock identity provider
- [x] Issuer and audience validated on every token
- [x] Clock skew bounded (≤300 seconds)
- [x] OAuth PKCE required for providers
- [x] Redirect URI exact allowlist
- [x] State and nonce validated on token exchange
- [ ] RevocationStore wired in production bootstrap
- [ ] Refresh token session metadata hashed per guidelines
- [ ] Cookie refresh transport with CSRF when implemented

## Authorization & Tenant Isolation

- [x] Permission dependencies on protected routes
- [x] Workspace header required on tenant routes
- [x] Repository layer workspace_id scoping
- [ ] Active membership verified before ActorContext
- [ ] RLS policies enabled in PostgreSQL
- [ ] Cross-tenant UUID guessing regression tests in CI

## API Security

- [ ] Security headers on all API responses
- [ ] Rate limits on auth endpoints
- [ ] Rate limits on upload endpoints
- [ ] Rate limits on generation endpoints
- [ ] Rate limits on publishing endpoints
- [x] Idempotency-Key validation
- [x] Problem+json errors without secret echo
- [ ] OpenAPI disabled in production
- [ ] SSRF-safe outbound HTTP client

## Upload & Storage

- [x] Extension allowlist
- [x] MIME prefix allowlist
- [x] Maximum size enforcement
- [x] Filename sanitization
- [x] Path traversal prevention
- [x] Checksum verification
- [x] SAS HTTPS-only with bounded expiry
- [ ] Virus scan before content usable
- [x] Azure account URL HTTPS required

## Worker Security

- [x] Bounded retry with exponential backoff
- [x] Poison message detection
- [x] Dead-letter queue isolation
- [ ] Celery message authentication
- [ ] Least-privilege worker actor per task type
- [x] Correlation ID propagation

## Provider Security

- [x] External token JWKS verification
- [x] Claim sanitization (no tokens in logs)
- [x] OAuth secrets repr=False
- [ ] Webhook signature verification
- [ ] Webhook replay deduplication

## Secret Management

- [x] Secrets via environment variables
- [x] Signing key repr=False
- [x] Storage connection string repr=False
- [x] AI API keys as SecretStr
- [ ] Azure Key Vault integration documented and wired
- [x] No production secrets in repository

## Logging & Observability

- [x] Authorization/token/password fields redacted
- [x] Exception args not serialized
- [x] Safe route labels for metrics
- [x] Identity logging excludes raw tokens
- [ ] Audit records for all material security actions

## Security Headers (Target)

Configure at API or edge:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Permissions-Policy: accelerometer=(), camera=(), geolocation=(), microphone=()
Cache-Control: no-store  (authenticated responses)
```

Validation helper: `cloud_content_hub.security.headers.validate_response_headers`

## Dependency & Supply Chain

- [x] pip-audit clean on project venv
- [ ] Lockfile committed
- [ ] SBOM generated in CI
- [ ] Image scanning in CI/CD
- [ ] Non-root container execution verified

## Automated Tests

- [x] Security test suite (`tests/security/`, 69 tests)
- [x] JWT hardening tests
- [x] OAuth validation tests
- [x] RBAC tests
- [x] Storage security tests
- [x] Logging redaction tests
- [x] Worker DLQ/retry tests
- [ ] CORS regression tests
- [ ] Webhook replay tests
- [ ] SSRF regression tests

## Pre-Release Gate

All items below must pass:

```bash
cd backend
python -m pytest tests/security -p no:benchmark -q
python -m ruff check src/cloud_content_hub/security tests/security
MYPYPATH=src python -m mypy src/cloud_content_hub/security
pip-audit .
```

**Production release blocked until R-001, R-002, and R-003 are resolved or explicitly accepted with compensating controls.**
