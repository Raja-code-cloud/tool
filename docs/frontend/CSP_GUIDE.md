# Content Security Policy Guide

Cloud Content Hub AI uses a **production Content Security Policy** applied via `next.config.ts` → `headers()` using `buildSecurityHeaders()` from `lib/security/headers.ts`.

## Policy summary (production)

```
default-src 'self';
script-src 'self';
style-src 'self' 'unsafe-inline';
img-src 'self' data: blob:;
font-src 'self';
connect-src 'self';
media-src 'self' blob:;
object-src 'none';
base-uri 'self';
form-action 'self';
frame-ancestors 'none';
worker-src 'self' blob:;
upgrade-insecure-requests;
```

## Documented exceptions

### `style-src 'unsafe-inline'` (required)

Tailwind CSS v4 and Next.js inject runtime styles. Removing `unsafe-inline` breaks layout and theme rendering. A nonce-based style policy would require middleware + layout wiring and is deferred to a future hardening pass.

### `script-src 'unsafe-eval' 'unsafe-inline'` (development only)

Next.js development HMR and React Fast Refresh require `unsafe-eval` and inline bootstrap scripts. These directives are **only** included when `NODE_ENV !== 'production'`.

Production `script-src` is restricted to `'self'` (no `unsafe-eval`).

### `blob:` and `data:` (required)

Upload wizard previews use `URL.createObjectURL()` (`blob:`) for images and video metadata. Character counts and inline SVG placeholders may use `data:` URIs.

## Future analytics

When analytics is integrated, add explicit domains to `connect-src` (and optionally `script-src` if using third-party tags):

```typescript
// Example — update lib/security/headers.ts
"connect-src 'self' https://www.google-analytics.com https://region1.google-analytics.com";
```

Prefer first-party proxy endpoints to minimize CSP surface area.

## Cross-Origin-Embedder-Policy (COEP)

**Not enabled.** The application does not require cross-origin isolation (SharedArrayBuffer, high-resolution timers). Enabling `require-corp` would interfere with blob preview URLs and any future third-party embeds.

## Testing CSP

1. Run a production build: `npm run build && npm run start`
2. Open DevTools → Network → select a document request → verify `Content-Security-Policy` header
3. Exercise upload previews, theme toggle, and wizard navigation
4. Check the browser console for CSP violations

## Report-only rollout (recommended for first production deploy)

For initial production deployment, consider temporarily emitting `Content-Security-Policy-Report-Only` alongside the enforcing policy. Add a `report-uri` or `report-to` endpoint when an observability pipeline is available.

## Nonce-based upgrade path

For stricter `script-src` without `unsafe-inline` in production:

1. Generate a per-request nonce in `middleware.ts`
2. Pass the nonce to the root layout via `x-nonce` request header
3. Apply `nonce={nonce}` to Next.js `<Script>` components
4. Set `script-src 'self' 'nonce-{nonce}' 'strict-dynamic'`

This requires coordination with the architecture team and is not part of the RC2 sprint.
