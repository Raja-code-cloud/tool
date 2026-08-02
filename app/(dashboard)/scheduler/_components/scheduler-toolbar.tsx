"use client";

import { Calendar, ChevronLeft, ChevronRight, RefreshCw } from "lucide-react";

import { OutlineButton, SecondaryButton } from "@/components/buttons";
import { Toolbar } from "@/components/common";
import { FilterGroup, FilterSearch, FilterSelect } from "@/components/filters";
import { Tabs } from "@/components/navigation";
import {
  SCHEDULE_STATUSES,
  SCHEDULER_PLATFORMS,
  SCHEDULER_TIMEZONES,
} from "@/lib/config/scheduler";
import type { PlatformId } from "@/lib/domain/platform";
import type { CalendarView, ScheduleStatus } from "@/lib/domain/scheduler";
import type { SchedulerFilters } from "@/lib/utils/scheduler";

export type SchedulerToolbarProps = {
  view: CalendarView;
  onViewChange: (view: CalendarView) => void;
  filters: SchedulerFilters;
  onFiltersChange: (patch: Partial<SchedulerFilters>) => void;
  timezone: string;
  onTimezoneChange: (timezone: string) => void;
  onToday: () => void;
  onPrevious: () => void;
  onNext: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
};

const VIEW_TABS = [
  { id: "month", label: "Month" },
  { id: "week", label: "Week" },
  { id: "day", label: "Day" },
  { id: "agenda", label: "Agenda" },
] as const;

export function SchedulerToolbar({
  view,
  onViewChange,
  filters,
  onFiltersChange,
  timezone,
  onTimezoneChange,
  onToday,
  onPrevious,
  onNext,
  onRefresh,
  isRefreshing,
}: SchedulerToolbarProps): React.JSX.Element {
  return (
    <div className="bg-card grid gap-3 rounded-xl border p-4">
      <Toolbar
        label="Scheduler controls"
        className="flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <Tabs
          items={[...VIEW_TABS]}
          value={view}
          onValueChange={(value) => onViewChange(value as CalendarView)}
          label="Calendar view"
          className="w-full sm:w-auto"
        />
        <div className="flex flex-wrap items-center gap-2">
          <SecondaryButton
            type="button"
            size="compact"
            onClick={onPrevious}
            aria-label="Previous period"
          >
            <ChevronLeft className="size-4" aria-hidden="true" />
          </SecondaryButton>
          <OutlineButton type="button" size="compact" onClick={onToday}>
            <Calendar className="size-4" aria-hidden="true" /> Today
          </OutlineButton>
          <SecondaryButton type="button" size="compact" onClick={onNext} aria-label="Next period">
            <ChevronRight className="size-4" aria-hidden="true" />
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
        label="Scheduler filter values"
        className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"
      >
        <FilterSearch
          placeholder="Search schedules…"
          value={filters.search}
          onChange={(event) => onFiltersChange({ search: event.target.value })}
          aria-label="Search schedules"
        />
        <FilterSelect
          id="scheduler-platform"
          label="Filter by platform"
          value={filters.platform}
          options={[
            { value: "all", label: "All platforms" },
            ...SCHEDULER_PLATFORMS.map(({ id, label }) => ({ value: id, label })),
          ]}
          onValueChange={(value) => onFiltersChange({ platform: value as PlatformId | "all" })}
        />
        <FilterSelect
          id="scheduler-status"
          label="Filter by status"
          value={filters.status}
          options={SCHEDULE_STATUSES}
          onValueChange={(value) => onFiltersChange({ status: value as ScheduleStatus | "all" })}
        />
        <FilterSelect
          id="scheduler-timezone"
          label="Timezone"
          value={timezone}
          options={SCHEDULER_TIMEZONES}
          onValueChange={onTimezoneChange}
        />
      </FilterGroup>
    </div>
  );
}
