# OWASP API Security Top 10 (2023) Validation

Review date: 2026-08-02  
Automated coverage: `backend/tests/security/`  
Programmatic mapping: `backend/src/cloud_content_hub/security/owasp.py`

## Summary

| Result         | Count |
| -------------- | ----- |
| Pass           | 0     |
| Partial        | 8     |
| Fail           | 2     |
| Not applicable | 0     |

## Validation Matrix

### API1:2023 — Broken Object Level Authorization

**Status:** Partial

**Validated controls:**

- Workspace-scoped repositories require explicit `workspace_id`
- Routes require `X-Workspace-ID` header and permission dependencies
- Composite foreign keys in schema enforce tenant-safe relationships

**Gaps:**

- Active workspace membership not verified at API boundary
- No cross-tenant UUID guessing regression in integration tests
- RLS not enabled in migrations

**Tests:** `test_workspace_isolation.py`, `test_api_authorization.py`

---

### API2:2023 — Broken Authentication

**Status:** Partial

**Validated controls:**

- RS256/ES256 only; HS256/none rejected at config
- Issuer allowlist, audience, expiry, clock skew (0–300s)
- Invalid bearer tokens logged and treated as anonymous; protected routes return 401
- Refresh token `jti` and RevocationStore protocol

**Gaps:**

- RevocationStore not wired in production bootstrap
- No JWT algorithm-confusion regression suite against live middleware
- Cookie refresh transport not implemented

**Tests:** `test_jwt_security.py`, `test_oauth_security.py`

---

### API3:2023 — Broken Object Property Level Authorization

**Status:** Partial

**Validated controls:**

- Pydantic models constrain request/response shapes
- Handler DTOs separate command/query types

**Gaps:**

- No automated mass-assignment tests for admin-only fields

**Tests:** Planned — add to `test_api_authorization.py`

---

### API4:2023 — Unrestricted Resource Consumption

**Status:** Fail

**Validated controls:**

- Idempotency-Key format validation (8–128 chars)
- Upload size limits in storage validators
- AI provider rate-limit error classification and retry

**Gaps:**

- No HTTP rate limiting middleware
- No per-workspace quotas for AI/upload/publish

**Tests:** `test_storage_security.py` (size limits only)

---

### API5:2023 — Broken Function Level Authorization

**Status:** Partial

**Validated controls:**

- `require_permission()`, `require_role()`, `current_admin()` dependencies
- Permission wildcards (`*`, `namespace:*`)

**Gaps:**

- Limited regression coverage for admin route denial

**Tests:** `test_rbac_security.py`, `test_api_authorization.py`

---

### API6:2023 — Unrestricted Access to Sensitive Business Flows

**Status:** Partial

**Validated controls:**

- OAuth PKCE and state validation
- Idempotency keys on mutating routes

**Gaps:**

- No step-up auth for OAuth linking or bulk export
- No rate limits on sensitive flows

**Tests:** `test_oauth_security.py`

---

### API7:2023 — Server Side Request Forgery

**Status:** Fail

**Validated controls:** None at platform level

**Gaps:**

- No outbound HTTP allowlist or private-range rejection

**Tests:** None — add SSRF regression when client wrapper exists

---

### API8:2023 — Security Misconfiguration

**Status:** Partial

**Validated controls:**

- Production rejects mock identity, wildcard CORS, insecure issuer
- OpenAPI optionally disabled via settings
- Duplicate httpx entry in pyproject (cosmetic)

**Gaps:**

- Security response headers not emitted
- No lockfile or SBOM in repository

**Tests:** `test_config_hardening.py`, `test_security_headers.py`

---

### API9:2023 — Improper Inventory Management

**Status:** Partial

**Validated controls:**

- Versioned `/api/v1` router
- Documented health/live/metrics endpoints
- OpenAPI structure documented

**Gaps:**

- No formal endpoint inventory with auth requirements

**Tests:** `test_api_authorization.py` (health/protected route sampling)

---

### API10:2023 — Unsafe Consumption of APIs

**Status:** Partial

**Validated controls:**

- External OAuth tokens verified via JWKS
- Provider claim sanitization
- Typed AI/storage adapters with bounded errors

**Gaps:**

- Webhook signature verification not implemented
- `webhook_receipt` model exists without handler

**Tests:** Provider contract tests in `tests/contract/`

## ASVS Mapping (Selected)

| ASVS Section | Topic              | Status                               |
| ------------ | ------------------ | ------------------------------------ |
| V2           | Authentication     | Partial                              |
| V3           | Session Management | Partial (JWT; no cookie sessions)    |
| V4           | Access Control     | Partial                              |
| V5           | Validation         | Pass (storage/input validators)      |
| V7           | Cryptography       | Pass (asymmetric JWT, HTTPS storage) |
| V8           | Data Protection    | Partial (redaction; no RLS)          |
| V9           | Communications     | Partial (TLS config; no HSTS at API) |
| V13          | API Security       | Partial                              |
| V14          | Configuration      | Partial                              |

## Regression Test Coverage

Run the full security suite:

```bash
cd backend && python -m pytest tests/security -p no:benchmark -v
```

Expected: **69 passed**
