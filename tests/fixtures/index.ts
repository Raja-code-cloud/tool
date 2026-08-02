/**
 * Stable, cross-suite fixture values. Prefer factories for mutable domain data.
 */
export const testFixture = {
  locale: "en-US",
  now: new Date("2025-01-15T12:00:00.000Z"),
  timezone: "UTC",
} as const;
