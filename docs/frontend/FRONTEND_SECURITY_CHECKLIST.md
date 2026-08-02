# Frontend Security Checklist

Use this checklist before each production release. Items marked **Backend** require another engineering sprint.

## Secrets & configuration

- [x] No secrets in `NEXT_PUBLIC_*` variables
- [x] No hardcoded API keys, tokens, or connection strings in frontend source
- [x] Mock credentials in `constants/settings.ts` are masked placeholders only

## Output encoding & rendering

- [x] No `dangerouslySetInnerHTML` or direct `innerHTML`
- [x] No `eval`, `new Function`, or `document.write`
- [x] User text rendered through React escaped JSX
- [x] Markdown preview uses plain text (`whitespace-pre-wrap`), not HTML parsing

## Browser headers

- [x] Content-Security-Policy configured (`lib/security/headers.ts`)
- [x] `X-Frame-Options: DENY` / `frame-ancestors 'none'`
- [x] `X-Content-Type-Options: nosniff`
- [x] `Referrer-Policy` configured
- [x] `Permissions-Policy` configured
- [x] `Cross-Origin-Opener-Policy` configured
- [x] `Cross-Origin-Resource-Policy` configured
- [ ] **Deploy:** HSTS at CDN / load balancer ([Security Headers](./SECURITY_HEADERS.md))

## Upload validation (client)

- [x] Poster: MIME, extension, 10 MB limit
- [x] Article: MIME, extension, 10 MB limit
- [x] Video: MIME, extension, 500 MB limit
- [x] Thumbnail: MIME, extension, 5 MB limit
- [x] Filename length and character validation
- [x] Graceful toast errors on rejection
- [ ] **Backend:** Independent type, size, signature, and malware scanning

## Input bounds

- [x] Project name ≤ 200 characters
- [x] Description ≤ 2,000 characters
- [x] Tags ≤ 500 characters
- [x] Article content ≤ 50,000 characters (HTML `maxLength` + validation)

## Client storage

- [x] Draft data uses versioned envelopes with 7-day TTL
- [x] Schema validation on restore
- [x] Draft cleared on successful project creation
- [x] Sensitive drafts cleared on sign-out placeholder
- [x] Expired entries purged on app load
- [x] Theme preference only (non-sensitive) in localStorage

## External links

- [x] No `target="_blank"` without `rel="noopener noreferrer"` (none present today)
- [x] `externalLinkProps()` helper available for future links

## Error handling

- [x] Production errors redacted in `reportClientError()` (digest only)
- [x] Full errors logged only in development

## Dependencies

- [x] npm overrides for patched `postcss` and `sharp`
- [ ] Re-run `npm audit --omit=dev` before each release
- [ ] **CI:** Fail on new high/critical production vulnerabilities

## Authentication & authorization (**Backend** — not this sprint)

- [ ] **Backend:** Server-enforced authentication on dashboard routes (H-02)
- [ ] **Backend:** Role/workspace authorization on privileged screens (H-02)
- [ ] **Backend:** Security controls wired to server actions (H-03)
- [ ] **Backend:** Real sign-out invalidates server session (H-03)

## Deployment verification

- [ ] Confirm headers on production URL (not just localhost)
- [ ] CSP violation monitoring (report-only or RUM)
- [ ] Protected routes return redirect when unauthenticated (**Backend**)

## OWASP alignment

This checklist maps to OWASP Frontend Security best practices. Remaining gaps are explicitly backend-dependent and documented in [Security Hardening](./SECURITY_HARDENING.md).
