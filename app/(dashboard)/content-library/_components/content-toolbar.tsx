"use client";

import { LayoutGrid, List, RefreshCw } from "lucide-react";

import { IconButton } from "@/components/buttons";
import { FilterBar, FilterGroup, FilterSearch, FilterSelect } from "@/components/filters";
import { Button } from "@/components/ui";
import {
  CONTENT_PLATFORMS,
  CONTENT_STATUSES,
  CONTENT_TYPES,
  DATE_FILTERS,
  SORT_OPTIONS,
} from "@/lib/config/content-library";
import { cn } from "@/lib/utils/cn";

export type ViewMode = "grid" | "list";

export type ContentToolbarProps = {
  search: string;
  onSearchChange: (value: string) => void;
  typeFilter: string;
  onTypeFilterChange: (value: string) => void;
  statusFilter: string;
  onStatusFilterChange: (value: string) => void;
  platformFilter: string;
  onPlatformFilterChange: (value: string) => void;
  dateFilter: string;
  onDateFilterChange: (value: string) => void;
  sort: string;
  onSortChange: (value: string) => void;
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
  resultCount: number;
  onOpenFilters?: () => void;
};

export function ContentToolbar(props: ContentToolbarProps): React.JSX.Element {
  const {
    search,
    onSearchChange,
    typeFilter,
    onTypeFilterChange,
    statusFilter,
    onStatusFilterChange,
    platformFilter,
    onPlatformFilterChange,
    dateFilter,
    onDateFilterChange,
    sort,
    onSortChange,
    viewMode,
    onViewModeChange,
    onRefresh,
    isRefreshing,
    resultCount,
    onOpenFilters,
  } = props;

  return (
    <FilterBar label="Content library filters" className="grid gap-3">
      <div className="tablet:flex-row tablet:items-center flex flex-col gap-3">
        <FilterSearch
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search by title, tag, platform, or type…"
          className="tablet:max-w-sm tablet:flex-1"
          aria-label="Search content library"
        />
        <p className="text-small text-muted-foreground tablet:ml-auto" aria-live="polite">
          {resultCount} {resultCount === 1 ? "item" : "items"}
        </p>
      </div>

      <FilterGroup>
        {onOpenFilters ? (
          <Button
            type="button"
            variant="outline"
            size="compact"
            className="desktop:hidden"
            onClick={onOpenFilters}
          >
            Filters
          </Button>
        ) : null}

        <FilterSelect
          id="filter-type"
          label="Content type"
          value={typeFilter}
          onValueChange={onTypeFilterChange}
          options={CONTENT_TYPES}
          triggerClassName="min-w-32"
        />
        <FilterSelect
          id="filter-status"
          label="Status"
          value={statusFilter}
          onValueChange={onStatusFilterChange}
          options={CONTENT_STATUSES}
          triggerClassName="min-w-32"
        />
        <FilterSelect
          id="filter-platform"
          label="Platform"
          value={platformFilter}
          onValueChange={onPlatformFilterChange}
          options={CONTENT_PLATFORMS}
          className="tablet:grid hidden"
          triggerClassName="min-w-32"
        />
        <FilterSelect
          id="filter-date"
          label="Date"
          value={dateFilter}
          onValueChange={onDateFilterChange}
          options={DATE_FILTERS}
          className="wide:grid hidden"
          triggerClassName="min-w-32"
        />
        <FilterSelect
          id="filter-sort"
          label="Sort by"
          value={sort}
          onValueChange={onSortChange}
          options={SORT_OPTIONS}
          triggerClassName="min-w-32"
        />

        <div className="ml-auto flex items-center gap-1">
          <IconButton
            label="Grid view"
            icon={<LayoutGrid aria-hidden="true" />}
            aria-pressed={viewMode === "grid"}
            className={cn(viewMode === "grid" && "bg-accent text-foreground")}
            onClick={() => onViewModeChange("grid")}
          />
          <IconButton
            label="List view"
            icon={<List aria-hidden="true" />}
            aria-pressed={viewMode === "list"}
            className={cn(viewMode === "list" && "bg-accent text-foreground")}
            onClick={() => onViewModeChange("list")}
          />
          <IconButton
            label="Refresh"
            icon={
              <RefreshCw aria-hidden="true" className={isRefreshing ? "animate-spin" : undefined} />
            }
            onClick={onRefresh}
            disabled={isRefreshing}
          />
        </div>
      </FilterGroup>
    </FilterBar>
  );
}
