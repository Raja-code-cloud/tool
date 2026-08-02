import {
  DRAFT_STORAGE_TTL_MS,
  SENSITIVE_STORAGE_KEYS,
  STORAGE_SCHEMA_VERSION,
  THEME_STORAGE_KEY,
  THEME_STORAGE_TTL_MS,
} from "@/lib/security/constants";

export type StorageEnvelope<T> = {
  readonly version: typeof STORAGE_SCHEMA_VERSION;
  readonly expiresAt: number;
  readonly savedAt: string;
  readonly data: T;
};

export type StorageReadResult<T> =
  | { readonly ok: true; readonly data: T }
  | {
      readonly ok: false;
      readonly reason: "unavailable" | "expired" | "invalid" | "version_mismatch";
    };

function isBrowserStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function writeVersionedStorage<T>(
  key: string,
  data: T,
  ttlMs: number = DRAFT_STORAGE_TTL_MS,
): boolean {
  if (!isBrowserStorageAvailable()) return false;

  const envelope: StorageEnvelope<T> = {
    version: STORAGE_SCHEMA_VERSION,
    expiresAt: Date.now() + ttlMs,
    savedAt: new Date().toISOString(),
    data,
  };

  try {
    window.localStorage.setItem(key, JSON.stringify(envelope));
    return true;
  } catch {
    return false;
  }
}

export function readVersionedStorage<T>(
  key: string,
  isValidData: (value: unknown) => value is T,
): StorageReadResult<T> {
  if (!isBrowserStorageAvailable()) return { ok: false, reason: "unavailable" };

  const raw = window.localStorage.getItem(key);
  if (!raw) return { ok: false, reason: "invalid" };

  try {
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return { ok: false, reason: "invalid" };

    const envelope = parsed as Partial<StorageEnvelope<unknown>>;
    if (envelope.version !== STORAGE_SCHEMA_VERSION) {
      window.localStorage.removeItem(key);
      return { ok: false, reason: "version_mismatch" };
    }
    if (typeof envelope.expiresAt !== "number" || envelope.expiresAt <= Date.now()) {
      window.localStorage.removeItem(key);
      return { ok: false, reason: "expired" };
    }
    if (!isValidData(envelope.data)) {
      window.localStorage.removeItem(key);
      return { ok: false, reason: "invalid" };
    }

    return { ok: true, data: envelope.data };
  } catch {
    window.localStorage.removeItem(key);
    return { ok: false, reason: "invalid" };
  }
}

export function removeStorageKey(key: string): void {
  if (!isBrowserStorageAvailable()) return;
  window.localStorage.removeItem(key);
}

/** Clears sensitive client-side drafts. Theme preference is retained. */
export function clearSensitiveClientStorage(): void {
  if (!isBrowserStorageAvailable()) return;
  for (const key of SENSITIVE_STORAGE_KEYS) {
    window.localStorage.removeItem(key);
  }
}

/** Removes expired versioned entries for known storage keys. */
export function purgeExpiredClientStorage(): void {
  if (!isBrowserStorageAvailable()) return;

  const keysToCheck = [...SENSITIVE_STORAGE_KEYS, THEME_STORAGE_KEY] as const;
  for (const key of keysToCheck) {
    const raw = window.localStorage.getItem(key);
    if (!raw) continue;

    try {
      const parsed: unknown = JSON.parse(raw);
      if (!parsed || typeof parsed !== "object") continue;
      const envelope = parsed as Partial<StorageEnvelope<unknown>>;
      if (typeof envelope.expiresAt === "number" && envelope.expiresAt <= Date.now()) {
        window.localStorage.removeItem(key);
      }
    } catch {
      window.localStorage.removeItem(key);
    }
  }
}

export { DRAFT_STORAGE_TTL_MS, THEME_STORAGE_TTL_MS };
