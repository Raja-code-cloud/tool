# Frontend Security Hardening

Security hardening sprint deliverables for Cloud Content Hub AI (RC2 review remediation).

## Scope

This sprint addressed **frontend-only** security controls:

- Browser security headers and Content Security Policy
- Client-side upload validation (complementing future backend enforcement)
- Versioned, expiring localStorage for drafts and preferences
- Input length bounds on wizard fields
- Redacted client error reporting
- Dependency vulnerability remediation via npm overrides
- Centralized security utilities under `lib/security/`

## Out of scope (other engineers)

| Area                                                      | Owner                    |
| --------------------------------------------------------- | ------------------------ |
| Authentication / route guards                             | Authentication engineer  |
| Security control server actions (2FA, API keys, sign-out) | Authentication engineer  |
| Backend upload scanning & authorization                   | Backend engineer         |
| Architecture, accessibility, performance                  | Respective sprint owners |

## Security utilities

All shared logic lives in `lib/security/`:

| Module                 | Purpose                               |
| ---------------------- | ------------------------------------- |
| `constants.ts`         | Storage keys, TTLs, filename patterns |
| `headers.ts`           | CSP and browser security headers      |
| `input-limits.ts`      | Enforceable text field bounds         |
| `storage.ts`           | Versioned localStorage with expiry    |
| `upload-validation.ts` | File type, size, filename checks      |
| `error-reporting.ts`   | Redacted production error logging     |
| `external-links.ts`    | Safe `target="_blank"` helpers        |

## Verified clean (no changes required)

- No `NEXT_PUBLIC_*` secrets or credentials
- No `dangerouslySetInnerHTML`, `eval`, or unsafe markdown rendering
- No unsafe `target="_blank"` links (none present)
- React escaped JSX for user content

## Related documentation

- [CSP Guide](./CSP_GUIDE.md)
- [Security Headers](./SECURITY_HEADERS.md)
- [Dependency Security](./DEPENDENCY_SECURITY.md)
- [Frontend Security Checklist](./FRONTEND_SECURITY_CHECKLIST.md)

## Deployment note

Configure **Strict-Transport-Security** at the CDN / reverse proxy (see [Security Headers](./SECURITY_HEADERS.md)). Do not enable HSTS in Next.js for local development.

## Post-sprint score estimate

After this sprint (excluding backend-dependent items H-02, H-03):

| Category             | Status                          |
| -------------------- | ------------------------------- |
| Headers & CSP        | Configured                      |
| Upload validation    | Client limits enforced          |
| Storage lifecycle    | TTL, versioning, logout cleanup |
| Input bounds         | Enforced in UI + validation     |
| Dependencies         | Overrides applied; see audit    |
| Route authentication | **Pending** — backend engineer  |
