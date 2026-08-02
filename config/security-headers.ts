type SecurityHeader = {
  readonly key: string;
  readonly value: string;
};

/**
 * Builds production-ready browser security headers for Next.js.
 *
 * CSP exceptions documented in docs/frontend/CSP_GUIDE.md:
 * - style-src 'unsafe-inline' — required by Tailwind CSS and Next.js injected styles
 * - script-src 'unsafe-inline' — required by Next.js App Router hydration bootstrap scripts
 *   until nonce-based CSP middleware is adopted
 * - img-src blob: — upload preview URLs in the upload wizard
 */
export function buildContentSecurityPolicy(isDev: boolean): string {
  const directives = [
    "default-src 'self'",
    isDev ? "script-src 'self' 'unsafe-inline' 'unsafe-eval'" : "script-src 'self' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline'",
    "font-src 'self' data:",
    "img-src 'self' data: blob:",
    "media-src 'self' blob:",
    "connect-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
  ];

  if (!isDev) {
    directives.push("upgrade-insecure-requests");
  }

  return directives.join("; ");
}

export function buildPermissionsPolicy(): string {
  return [
    "accelerometer=()",
    "autoplay=()",
    "camera=()",
    "cross-origin-isolated=()",
    "display-capture=()",
    "encrypted-media=()",
    "fullscreen=(self)",
    "geolocation=()",
    "gyroscope=()",
    "magnetometer=()",
    "microphone=()",
    "midi=()",
    "payment=()",
    "picture-in-picture=()",
    "publickey-credentials-get=()",
    "screen-wake-lock=()",
    "sync-xhr=()",
    "usb=()",
    "web-share=()",
    "xr-spatial-tracking=()",
  ].join(", ");
}

export function getSecurityHeaders(isDev: boolean): readonly SecurityHeader[] {
  const headers: SecurityHeader[] = [
    { key: "Content-Security-Policy", value: buildContentSecurityPolicy(isDev) },
    { key: "X-Frame-Options", value: "DENY" },
    { key: "X-Content-Type-Options", value: "nosniff" },
    { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
    { key: "Permissions-Policy", value: buildPermissionsPolicy() },
    { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
    { key: "Cross-Origin-Resource-Policy", value: "same-origin" },
    { key: "X-DNS-Prefetch-Control", value: "off" },
  ];

  if (!isDev) {
    headers.push({
      key: "Strict-Transport-Security",
      value: "max-age=63072000; includeSubDomains; preload",
    });
  }

  return headers;
}

/** COEP is intentionally omitted — it would break blob: media previews and future third-party embeds. */

export type { SecurityHeader };
