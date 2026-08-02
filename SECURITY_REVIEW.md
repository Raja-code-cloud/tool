# Frontend Security Review

Review date: 2026-08-02  
Scope: frontend application code and configuration, with repository documentation reviewed for security expectations.

## Executive Summary

The frontend is **not production-ready** from a security perspective. No committed frontend secrets, unsafe HTML rendering, cookie-based client persistence, or unsafe `target="_blank"` links were found. React's normal escaped rendering is used consistently, and upload controls define file-type and size restrictions.

Eight evidence-backed issues require attention: three high-severity production blockers, four medium-severity gaps, and one low-severity information-disclosure risk.

No application or business logic was changed during this review.

## Critical Issues

No critical issues found.

## High Issues

### H-01 — Known vulnerable production dependencies

**Evidence**

- `package.json:33` declares Next.js with a broad `^15.1.0` range.
- The installed tree contains `next@15.5.22`, `postcss@8.4.31`, and `sharp@0.34.5`.
- `npm audit --omit=dev` reports three high-severity production findings:
  - PostCSS arbitrary file read/information disclosure, `GHSA-6g55-p6wh-862q`
  - PostCSS path traversal/source-map disclosure, `GHSA-r28c-9q8g-f849`
  - sharp/libvips inherited vulnerabilities, `GHSA-f88m-g3jw-g9cj`

**Risk**

Affected transitive packages process CSS and images during application build/runtime workflows. Exploitability depends on whether attacker-controlled CSS, source maps, or images reach those processing paths, but vulnerable production packages should not be shipped.

**Recommendation**

Upgrade Next.js to a supported release whose dependency tree resolves to patched PostCSS and sharp versions. If the framework does not yet provide a compatible resolution, evaluate narrowly pinned package-manager overrides (`postcss` newer than `8.5.17`, `sharp` `0.35.0` or newer) with full build and image-processing tests. Do not use the audit tool's suggested downgrade to Next.js 9.3.3.

### H-02 — Dashboard routes have no authentication or authorization enforcement

**Evidence**

- `app/(dashboard)/layout.tsx:8-13` renders every dashboard child directly inside the workspace shell.
- No frontend middleware file or route guard was found.
- No `auth`, `useSession`, `getServerSession`, or equivalent access-control integration was found in frontend code.
- Sensitive-looking areas such as settings, API-key management, active sessions, social accounts, analytics, and content are reachable under the same unguarded route group.

**Risk**

When deployed as-is, users can navigate directly to dashboard URLs and render sensitive workspace UI without a frontend route-level authorization decision. Hiding navigation is not an access-control boundary.

**Recommendation**

Before production, enforce authentication at the dashboard route boundary using server-side session validation or framework middleware. Apply authorization checks to privileged settings and workspace-scoped routes. Backend APIs must independently authorize every request; frontend guards are defense in depth and prevent sensitive UI/data prefetch from being exposed.

### H-03 — Security-sensitive controls are client-only mocks

**Evidence**

- `app/(dashboard)/settings/_components/security-section.tsx:15-22` changes 2FA, SSO, and session state only in React state.
- `app/(dashboard)/settings/_components/api-keys-section.tsx:25-29` “revokes” keys only by filtering a client-side mock array.
- `app/(dashboard)/settings/_components/danger-zone-section.tsx:54-78` destructive actions only display success toasts.
- `components/layout/workspace-shell.tsx:118-129` renders sign-out without a logout handler.

**Risk**

Production users could believe that 2FA, SSO enforcement, session/key revocation, sign-out, and destructive actions succeeded when no server-side security state changed.

**Recommendation**

Do not expose these controls as operational until authenticated server actions confirm success. Disable or clearly label unavailable controls in production.

## Medium Issues

### M-01 — Browser security headers are not configured

**Evidence**

- `next.config.ts:3-9` enables strict mode and removes `X-Powered-By`, but defines no response headers.
- No frontend middleware applies security headers.
- No Content Security Policy, `frame-ancestors`, `X-Frame-Options`, `Referrer-Policy`, or `Permissions-Policy` was found.

**Risk**

The deployment lacks application-controlled defense in depth against script injection, clickjacking, referrer leakage, and unnecessary browser capabilities. Platform-level headers may exist, but they are not represented or testable in this repository.

**Recommendation**

Add and test a production header policy at one controlled edge:

- CSP with restrictive defaults and explicit allowances required by Next.js
- `frame-ancestors 'none'` (and `X-Frame-Options: DENY` for legacy clients)
- `Referrer-Policy: strict-origin-when-cross-origin` or stricter
- A least-privilege `Permissions-Policy`
- `X-Content-Type-Options: nosniff`

Prefer a nonce- or hash-based CSP. Deploy CSP in report-only mode first and avoid broad `unsafe-eval`/`unsafe-inline` allowances in production.

### M-02 — Content drafts persist in origin-wide localStorage

**Evidence**

- `app/(dashboard)/upload/_components/use-wizard-state.ts:133-145` serializes the upload wizard form to `localStorage`.
- `app/(dashboard)/upload/_components/wizard-types.ts:12-34` shows that the persisted form can include project metadata, descriptions, tags, scheduling data, and pasted article content.
- File bytes and object URLs are correctly excluded, but file names, sizes, and MIME types remain in the stored draft.
- Data is removed only by the explicit reset path at `use-wizard-state.ts:148-160`; no expiry, user/workspace binding, logout cleanup, or automatic post-submit cleanup is evident.

**Risk**

Draft content remains readable by any JavaScript executing on the origin, by later users of a shared browser profile, and potentially after account/workspace changes. This increases the impact of a future XSS or local device compromise.

**Recommendation**

Avoid persisting article bodies or other confidential content in localStorage. If local draft persistence is required, minimize fields, bind records to the authenticated user/workspace, add a short expiry and schema validation, and clear drafts on logout and successful submission. Treat client-side encryption with a client-accessible key as obfuscation, not a security boundary.

### M-03 — Upload validation is client-only and incomplete

**Evidence**

- `components/upload/upload.tsx:21-27` delegates checks to bypassable `react-dropzone` validation.
- `constants/upload-wizard.ts:75-86` defines MIME/extension allowlists and size caps for posters, video, and thumbnails, but the article upload has no maximum size.
- No content-signature or malware validation is present in frontend code.

**Risk**

Client MIME, filename, and size checks can be bypassed by direct requests. The uncapped article path can also consume excessive client memory.

**Recommendation**

Add an article size limit and rejection feedback. Independently enforce type, byte limits, content signatures, safe filenames, and malware scanning at the upload service.

### M-04 — User input validation lacks enforceable bounds and schemas

**Evidence**

- `app/(dashboard)/upload/_components/wizard-types.ts:75-119` has no maximum lengths for project name, description, tags, or article content.
- The UI displays a 50,000-character article count, but the textarea and validation logic do not enforce it.
- `zod`, `react-hook-form`, and `@hookform/resolvers` are installed but unused by application code.

**Risk**

Once connected to APIs, unbounded values can cause oversized requests, storage abuse, parser stress, and inconsistent validation.

**Recommendation**

Define allowlist-based schemas with explicit bounds, enforce corresponding HTML limits, and mirror all constraints server-side. Schema-validate any future localStorage restore.

## Low Issues

### L-01 — Full client errors are written to the browser console

**Evidence**

- `app/(dashboard)/error.tsx:8-12` calls `console.error(error)` with complete `Error` objects.

**Risk**

Production errors may disclose internal paths or implementation details in browser developer tools.

**Recommendation**

Use a redacting observability client and send only approved metadata; retain an opaque incident identifier for users.

The localhost credentials in `backend/.env.example` are explicit development examples and are outside the frontend scope. They are not production secrets, but must never be reused in deployed environments.

## Recommendations

Priority order:

1. Resolve the audited production dependency vulnerabilities and regenerate the lockfile.
2. Add server-enforced authentication and authorization at protected route boundaries.
3. Connect security-sensitive controls to authenticated server actions or disable them.
4. Define, deploy, and test the browser security-header policy.
5. Enforce upload and input limits on both client and server.
6. Reduce and expire locally persisted upload-draft content.
7. Add CI gates for production dependency auditing, secret scanning, security-header tests, and protected-route tests.
8. Re-run this review against the production deployment because CDN/hosting headers and authentication redirects cannot be fully verified from source alone.

## OWASP Frontend Checklist

- [x] No hardcoded frontend API keys, bearer tokens, passwords, private keys, or production connection strings found.
- [x] Mock API-key values are masked placeholders, not usable credentials (`constants/settings.ts:149-153`).
- [x] No `dangerouslySetInnerHTML`, direct `innerHTML`, `document.write`, `eval`, or `new Function` usage found.
- [x] User-controlled text is rendered through React's escaped JSX paths.
- [x] No unsafe `target="_blank"` usage found; no such external-link targets are currently present.
- [x] No client-side cookie writes or sessionStorage usage found.
- [x] Theme localStorage persistence contains only a non-sensitive theme choice.
- [ ] Sensitive content persistence is minimized and lifecycle-bound.
- [x] Upload UI restricts accepted extensions/MIME declarations and image/video sizes.
- [ ] All upload classes have an explicit client size limit; the article upload currently has no configured maximum.
- [ ] Uploaded content is treated as untrusted and independently validated/scanned server-side (not verifiable in frontend scope).
- [ ] Free-text inputs enforce explicit maximum lengths with validated schemas.
- [x] No `NEXT_PUBLIC_*` variables or arbitrary frontend `process.env` reads were found.
- [ ] Protected routes enforce authentication before rendering.
- [ ] Privileged screens enforce role/workspace authorization before rendering.
- [ ] CSP is configured and tested.
- [ ] Clickjacking protection is configured.
- [ ] Referrer and permissions policies are configured.
- [ ] Production dependency audit is clean.
- [ ] Security controls are verified in the deployed response, not only source configuration.

## Frontend Security Score

**50 / 100**

Scoring rationale: strong baseline React output encoding and no exposed frontend secrets, reduced by vulnerable dependencies, absent route protection, non-operational security controls, missing headers, incomplete upload/input validation, and sensitive local persistence.

## Production Readiness

**Not ready for production.**

Release should be blocked until H-01, H-02, and H-03 are resolved. M-01 should also be completed before public deployment. M-02 through M-04 require documented controls before handling confidential or untrusted content.

### Review limitations

- This was a source and dependency-tree review; no deployed environment was available for response-header, cookie-attribute, redirect, CDN, or runtime penetration testing.
- Backend authorization, malware scanning, content-type sniffing, and upload storage controls were not assessed because backend changes and review were excluded.
- Unused-package status was not treated as a vulnerability without evidence. No package was removed during this security-only sprint.
