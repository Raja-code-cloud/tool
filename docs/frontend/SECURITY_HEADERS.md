# Security Headers

Browser security headers are configured in `next.config.ts` using `buildSecurityHeaders()` from `lib/security/headers.ts`. They apply to all routes via `/:path*`.

## Headers applied

| Header                         | Production value                  | Purpose                                  |
| ------------------------------ | --------------------------------- | ---------------------------------------- |
| `Content-Security-Policy`      | See [CSP Guide](./CSP_GUIDE.md)   | Mitigate XSS, injection, framing         |
| `X-Frame-Options`              | `DENY`                            | Clickjacking protection (legacy clients) |
| `X-Content-Type-Options`       | `nosniff`                         | Prevent MIME sniffing                    |
| `Referrer-Policy`              | `strict-origin-when-cross-origin` | Limit referrer leakage                   |
| `Permissions-Policy`           | Least-privilege (see source)      | Disable unused browser APIs              |
| `Cross-Origin-Opener-Policy`   | `same-origin`                     | Isolate browsing context                 |
| `Cross-Origin-Resource-Policy` | `same-origin`                     | Restrict cross-origin resource loads     |

## Headers intentionally omitted

| Header                         | Reason                                                 |
| ------------------------------ | ------------------------------------------------------ |
| `Cross-Origin-Embedder-Policy` | Not required; would break blob upload previews         |
| `Strict-Transport-Security`    | Must be set at CDN / load balancer (see below)         |
| `X-Powered-By`                 | Removed via `poweredByHeader: false` in Next.js config |

## Strict-Transport-Security (deployment guidance)

**Do not** set HSTS in Next.js application code. Configure it at the edge:

### Example (nginx)

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

### Example (Vercel)

Add to `vercel.json`:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000; includeSubDomains; preload"
        }
      ]
    }
  ]
}
```

### Requirements before enabling HSTS

- Valid TLS certificate on all environments users can reach
- All subdomains served over HTTPS
- `includeSubDomains` only when every subdomain supports HTTPS
- Submit to HSTS preload list only after sustained production validation

## Verification

```bash
npm run build
npm run start
curl -I http://localhost:3000/
```

Confirm each header appears on HTML document responses. Re-test after CDN deployment because edge headers may merge with or override application headers.

## Development vs production

`buildSecurityHeaders(isDev)` adjusts CSP:

- **Development:** allows `unsafe-eval` and `unsafe-inline` in `script-src` for HMR
- **Production:** strict `script-src 'self'`; adds `upgrade-insecure-requests`
