"use client";

import { Download, RefreshCw } from "lucide-react";

import { SecondaryButton } from "@/components/buttons";
import { Toolbar } from "@/components/common";
import { FilterGroup, FilterSearch, FilterSelect } from "@/components/filters";
import type { AnalyticsDateRange, DateRangeOption, PlatformFilterOption } from "@/lib/domain/analytics";
import type { PlatformId } from "@/lib/domain/platform";
import type { AnalyticsFilters } from "@/lib/utils/analytics";

export type AnalyticsFiltersBarProps = {
  filters: AnalyticsFilters;
  dateLabel: string;
  dateRangeOptions: readonly DateRangeOption[];
  platformFilterOptions: readonly PlatformFilterOption[];
  search: string;
  onSearchChange: (value: string) => void;
  onDateRangeChange: (range: AnalyticsDateRange) => void;
  onPlatformChange: (platform: PlatformId | "all") => void;
  onRefresh: () => void;
  onExportCsv: () => void;
  isRefreshing: boolean;
  canExport: boolean;
};

export function AnalyticsFiltersBar({
  filters,
  dateLabel,
  dateRangeOptions,
  platformFilterOptions,
  search,
  onSearchChange,
  onDateRangeChange,
  onPlatformChange,
  onRefresh,
  onExportCsv,
  isRefreshing,
  canExport,
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
        <div className="flex flex-wrap gap-2">
          <SecondaryButton
            type="button"
            size="compact"
            onClick={onExportCsv}
            disabled={!canExport || isRefreshing}
          >
            <Download className="size-4" aria-hidden="true" /> Export CSV
          </SecondaryButton>
          <SecondaryButton type="button" size="compact" onClick={onRefresh} disabled={isRefreshing}>
            <RefreshCw
              className={`size-4 ${isRefreshing ? "animate-spin" : ""}`}
              aria-hidden="true"
            />{" "}
            Refresh
          </SecondaryButton>
        </div>
      </Toolbar>
      <FilterGroup
        label="Analytics filter values"
        className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3"
      >
        <FilterSelect
          id="analytics-date-range"
          label="Date range"
          value={filters.dateRange}
          options={dateRangeOptions}
          onValueChange={(value) => onDateRangeChange(value as AnalyticsDateRange)}
        />
        <FilterSelect
          id="analytics-platform"
          label="Platform filter"
          value={filters.platform}
          options={platformFilterOptions}
          onValueChange={(value) => onPlatformChange(value as PlatformId | "all")}
        />
        <FilterSearch
          placeholder="Search posts…"
          aria-label="Search analytics"
          className="w-full"
          value={search}
          onValueChange={onSearchChange}
        />
      </FilterGroup>
      {filters.dateRange === "custom" && (
        <p className="text-muted-foreground mt-2 text-xs">
          Custom range defaults to the last 30 days until a date picker is added.
        </p>
      )}
    </div>
  );
}
