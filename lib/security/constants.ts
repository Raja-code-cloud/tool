/** Current schema version for versioned client storage envelopes. */
export const STORAGE_SCHEMA_VERSION = 1 as const;

/** Default TTL for sensitive draft data (7 days). */
export const DRAFT_STORAGE_TTL_MS = 7 * 24 * 60 * 60 * 1000;

/** Theme preference is non-sensitive; long TTL is acceptable. */
export const THEME_STORAGE_TTL_MS = 365 * 24 * 60 * 60 * 1000;

/** Maximum filename length accepted by client upload validation. */
export const MAX_FILENAME_LENGTH = 255;

/** Safe filename pattern: alphanumeric, spaces, dots, dashes, underscores. */
export const SAFE_FILENAME_PATTERN = /^[\w\s.\-()]+$/;

/** Storage keys managed by security cleanup routines. */
export const SENSITIVE_STORAGE_KEYS = ["cch:upload-wizard-draft"] as const;

export const THEME_STORAGE_KEY = "app-theme" as const;
