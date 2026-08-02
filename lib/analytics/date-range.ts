import type { AnalyticsDateRange } from "@/lib/domain/analytics";

export type AnalyticsPeriod = {
  readonly periodStart: string;
  readonly periodEnd: string;
};

function toIso(date: Date): string {
  return date.toISOString();
}

function startOfDay(date: Date): Date {
  const next = new Date(date);
  next.setHours(0, 0, 0, 0);
  return next;
}

function endOfDay(date: Date): Date {
  const next = new Date(date);
  next.setHours(23, 59, 59, 999);
  return next;
}

/** Converts UI date presets into RFC 3339 bounds for analytics API calls. */
export function resolveAnalyticsPeriod(
  dateRange: AnalyticsDateRange,
  customPeriod?: AnalyticsPeriod,
): AnalyticsPeriod {
  const now = new Date();
  const end = endOfDay(now);

  if (dateRange === "custom" && customPeriod) {
    return customPeriod;
  }

  switch (dateRange) {
    case "today":
      return { periodStart: toIso(startOfDay(now)), periodEnd: toIso(end) };
    case "7d": {
      const start = new Date(now);
      start.setDate(start.getDate() - 6);
      return { periodStart: toIso(startOfDay(start)), periodEnd: toIso(end) };
    }
    case "30d": {
      const start = new Date(now);
      start.setDate(start.getDate() - 29);
      return { periodStart: toIso(startOfDay(start)), periodEnd: toIso(end) };
    }
    case "90d": {
      const start = new Date(now);
      start.setDate(start.getDate() - 89);
      return { periodStart: toIso(startOfDay(start)), periodEnd: toIso(end) };
    }
    case "custom":
    default: {
      const start = new Date(now);
      start.setDate(start.getDate() - 29);
      return { periodStart: toIso(startOfDay(start)), periodEnd: toIso(end) };
    }
  }
}
