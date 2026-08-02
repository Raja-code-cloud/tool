"use client";

import { useMemo, useState } from "react";

import type { AnalyticsDateRange } from "@/lib/domain/analytics";
import type { PlatformId } from "@/lib/domain/platform";
import { analyticsService } from "@/lib/services";
import type { AnalyticsFilters } from "@/lib/services/workspace-services";

export function useAnalyticsFilters() {
  const [filters, setFilters] = useState<AnalyticsFilters>({
    dateRange: "30d",
    platform: "all",
  });

  const patchFilters = (patch: Partial<AnalyticsFilters>) => {
    setFilters((prev) => ({ ...prev, ...patch }));
  };

  const dateLabel = useMemo(() => {
    const option = analyticsService
      .getDateRangeOptions()
      .find((item) => item.value === filters.dateRange);
    return option?.label ?? filters.dateRange;
  }, [filters.dateRange]);

  return {
    filters,
    patchFilters,
    dateLabel,
    setPlatform: (platform: PlatformId | "all") => patchFilters({ platform }),
    setDateRange: (dateRange: AnalyticsDateRange) => patchFilters({ dateRange }),
  };
}
