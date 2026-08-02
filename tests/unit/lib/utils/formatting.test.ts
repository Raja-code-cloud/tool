import { describe, expect, it } from "vitest";

import {
  formatBytes,
  formatCompactNumber,
  formatCurrency,
  formatDate,
  formatDateTime,
  formatNumber,
  formatPercent,
  formatRelativeTime,
  formatTime,
} from "@/lib/utils/formatting";

describe("formatting utilities", () => {
  it("formats numbers and currency with locale awareness", () => {
    expect(formatNumber(1234.5, { locale: "en-US" })).toBe("1,234.5");
    expect(formatCurrency(42, "USD", { locale: "en-US" })).toBe("$42.00");
    expect(formatCompactNumber(1_250_000, { locale: "en-US" })).toMatch(/1\.3M|1\.2M/);
  });

  it("formats percentages from ratio and percent inputs", () => {
    expect(formatPercent(0.425)).toBe("42.5%");
    expect(formatPercent(42.5, { input: "percent" })).toBe("42.5%");
  });

  it("formats dates, times, and combined date-times", () => {
    const iso = "2026-01-15T14:30:00.000Z";
    expect(formatDate(iso, { locale: "en-US" })).toMatch(/Jan/);
    expect(formatTime(iso, { locale: "en-US", timeZone: "UTC" })).toMatch(/\d/);
    expect(formatDateTime(iso, { locale: "en-US" })).toMatch(/Jan/);
  });

  it("formats relative time against a fixed reference clock", () => {
    const target = "2026-01-15T12:00:00.000Z";
    const now = new Date("2026-01-15T12:05:00.000Z").getTime();
    expect(formatRelativeTime(target, { now, locale: "en-US" })).toMatch(/5 minutes ago|minute/i);
  });

  it("formats byte sizes with sane fallbacks", () => {
    expect(formatBytes(0)).toBe("0 B");
    expect(formatBytes(1024)).toBe("1 KB");
    expect(formatBytes(1_572_864)).toBe("1.5 MB");
    expect(formatBytes(-1)).toBe("0 B");
    expect(formatBytes(Number.NaN)).toBe("0 B");
  });
});
