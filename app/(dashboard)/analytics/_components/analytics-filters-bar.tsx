"use client";

import { RefreshCw } from "lucide-react";

import { SecondaryButton } from "@/components/buttons";
import { Toolbar } from "@/components/common";
import { FilterGroup, FilterSearch, FilterSelect } from "@/components/filters";
import type { AnalyticsDateRange } from "@/lib/domain/analytics";
import type { PlatformId } from "@/lib/domain/platform";
import { analyticsService } from "@/lib/services";
import type { AnalyticsFilters } from "@/lib/utils/analytics";

export type AnalyticsFiltersBarProps = {
  filters: AnalyticsFilters;
  dateLabel: string;
  onDateRangeChange: (range: AnalyticsDateRange) => void;
  onPlatformChange: (platform: PlatformId | "all") => void;
  onRefresh: () => void;
  isRefreshing: boolean;
};

export function AnalyticsFiltersBar({
  filters,
  dateLabel,
  onDateRangeChange,
  onPlatformChange,
  onRefresh,
  isRefreshing,
}: AnalyticsFiltersBarProps): React.JSX.Element {
  return (
    <div className="bg-card rounded-xl border p-4">
      <Toolbar
        label="Analytics filters"
        className="flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <p className="text-muted-foreground text-sm">
          Showing <span className="text-foreground font-semibold">{dateLabel}</span> across all
          connected platforms.
        </p>
        <SecondaryButton type="button" size="compact" onClick={onRefresh} disabled={isRefreshing}>
          <RefreshCw
            className={`size-4 ${isRefreshing ? "animate-spin" : ""}`}
            aria-hidden="true"
          />{" "}
          Refresh
        </SecondaryButton>
      </Toolbar>
      <FilterGroup
        label="Analytics filter values"
        className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3"
      >
        <FilterSelect
          id="analytics-date-range"
          label="Date range"
          value={filters.dateRange}
          options={analyticsService.getDateRangeOptions()}
          onValueChange={(value) => onDateRangeChange(value as AnalyticsDateRange)}
        />
        <FilterSelect
          id="analytics-platform"
          label="Platform filter"
          value={filters.platform}
          options={analyticsService.getPlatformFilterOptions()}
          onValueChange={(value) => onPlatformChange(value as PlatformId | "all")}
        />
        <FilterSearch
          placeholder="Search posts…"
          aria-label="Search analytics"
          className="w-full"
        />
      </FilterGroup>
      {filters.dateRange === "custom" && (
        <p className="text-muted-foreground mt-2 text-xs">
          Custom range uses the last 30 days of mock data.
        </p>
      )}
    </div>
  );
}
