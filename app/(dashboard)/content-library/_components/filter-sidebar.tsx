"use client";

import { SIDEBAR_FILTERS } from "@/lib/config/content-library";
import type { SidebarFilterId } from "@/lib/domain/content";
import { cn } from "@/lib/utils/cn";

export type FilterSidebarProps = {
  activeFilter: SidebarFilterId;
  onFilterChange: (filterId: SidebarFilterId) => void;
  counts: Record<SidebarFilterId, number>;
  className?: string;
};

export function FilterSidebar({
  activeFilter,
  onFilterChange,
  counts,
  className,
}: FilterSidebarProps): React.JSX.Element {
  return (
    <nav aria-label="Content filters" className={cn("flex flex-col gap-1", className)}>
      {SIDEBAR_FILTERS.map((filter) => {
        const isActive = activeFilter === filter.id;
        return (
          <button
            key={filter.id}
            type="button"
            onClick={() => onFilterChange(filter.id)}
            aria-current={isActive ? "true" : undefined}
            className={cn(
              "hover:bg-accent hover:text-foreground focus-visible:ring-ring flex min-h-9 items-center justify-between gap-2 rounded-md px-3 py-2 text-left text-sm font-medium transition-colors duration-(--duration-fast) focus-visible:ring-2 focus-visible:outline-none",
              isActive ? "bg-accent text-foreground font-semibold" : "text-muted-foreground",
            )}
          >
            <span>{filter.label}</span>
            <span className="text-small text-muted-foreground tabular-nums">
              {counts[filter.id] ?? 0}
            </span>
          </button>
        );
      })}
    </nav>
  );
}
