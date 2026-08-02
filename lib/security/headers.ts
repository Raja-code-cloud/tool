/**
 * Production browser security headers for Next.js `headers()` configuration.
 * CSP exceptions are documented in docs/frontend/CSP_GUIDE.md.
 */

export type SecurityHeader = {
  readonly key: string;
  readonly value: string;
};

const PERMISSIONS_POLICY = [
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

function buildContentSecurityPolicy(isDev: boolean): string {
  const directives = [
    "default-src 'self'",
    // Next.js production bundles are same-origin; dev HMR requires unsafe-eval (documented exception).
    isDev ? "script-src 'self' 'unsafe-eval' 'unsafe-inline'" : "script-src 'self'",
    // Tailwind and Next.js inject runtime styles; unsafe-inline is required (documented exception).
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "font-src 'self'",
    "connect-src 'self'",
    "media-src 'self' blob:",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "worker-src 'self' blob:",
  ];

  if (!isDev) {
    directives.push("upgrade-insecure-requests");
  }

  return directives.join("; ");
}

/** Builds the full security header set for a given runtime environment. */
export function buildSecurityHeaders(
  isDev: boolean = process.env.NODE_ENV !== "production",
): readonly SecurityHeader[] {
  return [
    { key: "Content-Security-Policy", value: buildContentSecurityPolicy(isDev) },
    { key: "X-Frame-Options", value: "DENY" },
    { key: "X-Content-Type-Options", value: "nosniff" },
    { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
    { key: "Permissions-Policy", value: PERMISSIONS_POLICY },
    { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
    { key: "Cross-Origin-Resource-Policy", value: "same-origin" },
    // COEP omitted: app does not require cross-origin isolation (would break Google Fonts / blob previews).
  ];
}

/** Flat record form for tests and documentation tooling. */
export function securityHeadersRecord(isDev?: boolean): Record<string, string> {
  return Object.fromEntries(buildSecurityHeaders(isDev).map(({ key, value }) => [key, value]));
}
