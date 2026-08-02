import {
  readVersionedStorage,
  removeStorageKey,
  writeVersionedStorage,
} from "@/lib/security/storage";

const ACCESS_TOKEN_KEY = "cch:access-token";
/** Access token TTL buffer — refresh 60s before expiry. */
const REFRESH_BUFFER_MS = 60_000;

export type StoredAccessToken = {
  readonly accessToken: string;
  readonly expiresAt: number;
};

function isStoredAccessToken(value: unknown): value is StoredAccessToken {
  if (!value || typeof value !== "object") return false;
  const record = value as Record<string, unknown>;
  return typeof record.accessToken === "string" && typeof record.expiresAt === "number";
}

/** In-memory cache for the current access token (fast path). */
let memoryToken: StoredAccessToken | null = null;

export function getAccessToken(): string | null {
  if (memoryToken && memoryToken.expiresAt > Date.now()) {
    return memoryToken.accessToken;
  }

  const stored = readVersionedStorage(ACCESS_TOKEN_KEY, isStoredAccessToken);
  if (!stored.ok) {
    memoryToken = null;
    return null;
  }

  if (stored.data.expiresAt <= Date.now()) {
    clearAccessToken();
    return null;
  }

  memoryToken = stored.data;
  return stored.data.accessToken;
}

export function setAccessToken(accessToken: string, expiresInSeconds: number): void {
  const expiresAt = Date.now() + expiresInSeconds * 1000;
  const stored: StoredAccessToken = { accessToken, expiresAt };
  memoryToken = stored;
  writeVersionedStorage(ACCESS_TOKEN_KEY, stored, expiresInSeconds * 1000 + REFRESH_BUFFER_MS);
}

export function clearAccessToken(): void {
  memoryToken = null;
  removeStorageKey(ACCESS_TOKEN_KEY);
}

export function isAccessTokenExpired(): boolean {
  const token = memoryToken ?? readVersionedStorage(ACCESS_TOKEN_KEY, isStoredAccessToken);
  if (token === null) return true;
  if (typeof token === "object" && "ok" in token) {
    if (!token.ok) return true;
    return token.data.expiresAt <= Date.now() + REFRESH_BUFFER_MS;
  }
  return token.expiresAt <= Date.now() + REFRESH_BUFFER_MS;
}

export function getCsrfToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(/(?:^|;\s*)cch_csrf=([^;]*)/);
  return match?.[1] ? decodeURIComponent(match[1]) : null;
}
