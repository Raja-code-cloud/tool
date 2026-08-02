import {
  formatCompactNumber as formatCanonicalCompactNumber,
  formatPercent as formatCanonicalPercent,
} from "@/lib/utils/formatting";

export type { AnalyticsFilters } from "@/lib/services/workspace-services";

/** Analytics chart/table compact number preset. */
export function formatCompactNumber(value: number): string {
  return formatCanonicalCompactNumber(value, value >= 1_000 ? { minimumFractionDigits: 1 } : {});
}

/** Analytics percent preset (input values are 0–100). */
export function formatPercent(value: number): string {
  return formatCanonicalPercent(value, {
    input: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
}
