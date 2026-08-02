import { describe, expect, it } from "vitest";

import { DRAFT_STORAGE_KEY } from "@/constants/upload-wizard";
import { STORAGE_SCHEMA_VERSION } from "@/lib/security/constants";
import { buildSecurityHeaders, securityHeadersRecord } from "@/lib/security/headers";
import { INPUT_LIMITS, isWithinLimit, limitExceededMessage } from "@/lib/security/input-limits";
import {
  clearSensitiveClientStorage,
  purgeExpiredClientStorage,
  readVersionedStorage,
  writeVersionedStorage,
} from "@/lib/security/storage";
import { validateFilename, validateUploadFile } from "@/lib/security/upload-validation";

describe("security headers", () => {
  it("includes core browser security headers in production mode", () => {
    const headers = securityHeadersRecord(false);
    expect(headers["X-Frame-Options"]).toBe("DENY");
    expect(headers["X-Content-Type-Options"]).toBe("nosniff");
    expect(headers["Referrer-Policy"]).toBe("strict-origin-when-cross-origin");
    expect(headers["Cross-Origin-Opener-Policy"]).toBe("same-origin");
    expect(headers["Cross-Origin-Resource-Policy"]).toBe("same-origin");
    expect(headers["Content-Security-Policy"]).toContain("frame-ancestors 'none'");
    expect(headers["Content-Security-Policy"]).not.toContain("unsafe-eval");
  });

  it("allows dev-only script exceptions for HMR", () => {
    const headers = securityHeadersRecord(true);
    expect(headers["Content-Security-Policy"]).toContain("'unsafe-eval'");
  });

  it("does not set COEP", () => {
    const headers = buildSecurityHeaders(false);
    expect(headers.find((header) => header.key === "Cross-Origin-Embedder-Policy")).toBeUndefined();
  });
});

describe("input limits", () => {
  it("enforces article content maximum", () => {
    const within = "a".repeat(INPUT_LIMITS.articleContent);
    expect(isWithinLimit(within, "articleContent")).toBe(true);
    expect(isWithinLimit(within + "b", "articleContent")).toBe(false);
    expect(limitExceededMessage("articleContent")).toContain("50,000");
  });
});

describe("upload validation", () => {
  it("rejects path traversal filenames", () => {
    expect(validateFilename("../secret.txt")).toMatch(/invalid path/);
  });

  it("rejects oversized poster files", () => {
    const file = new File([new Uint8Array(11 * 1024 * 1024)], "poster.png", { type: "image/png" });
    const result = validateUploadFile(file, "poster");
    expect(result.valid).toBe(false);
    if (!result.valid) expect(result.error).toContain("smaller");
  });

  it("accepts valid article files", () => {
    const file = new File(["# Hello"], "article.md", { type: "text/markdown" });
    expect(validateUploadFile(file, "article")).toEqual({ valid: true });
  });
});

describe("versioned storage", () => {
  it("expires and removes stale drafts", () => {
    const key = DRAFT_STORAGE_KEY;
    writeVersionedStorage(key, { form: { projectName: "test" } }, -1);
    const result = readVersionedStorage(
      key,
      (value): value is { form: { projectName: string } } => {
        return Boolean(value && typeof value === "object" && "form" in value);
      },
    );
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.reason).toBe("expired");
  });

  it("clears sensitive keys on logout cleanup", () => {
    writeVersionedStorage(DRAFT_STORAGE_KEY, { hello: "world" });
    clearSensitiveClientStorage();
    expect(window.localStorage.getItem(DRAFT_STORAGE_KEY)).toBeNull();
  });

  it("rejects schema version mismatches", () => {
    const key = "cch:test-version";
    window.localStorage.setItem(
      key,
      JSON.stringify({
        version: STORAGE_SCHEMA_VERSION + 1,
        expiresAt: Date.now() + 60_000,
        savedAt: new Date().toISOString(),
        data: { ok: true },
      }),
    );
    const result = readVersionedStorage(key, (value): value is { ok: boolean } => {
      return Boolean(value && typeof value === "object" && "ok" in value);
    });
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.reason).toBe("version_mismatch");
    window.localStorage.removeItem(key);
  });

  it("purges expired entries", () => {
    writeVersionedStorage(DRAFT_STORAGE_KEY, { hello: "world" }, -1);
    purgeExpiredClientStorage();
    expect(window.localStorage.getItem(DRAFT_STORAGE_KEY)).toBeNull();
  });
});
