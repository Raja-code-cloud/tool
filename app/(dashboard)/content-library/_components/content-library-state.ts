import type { SidebarFilterId } from "@/lib/domain/content";
import type { ToolbarFilters } from "@/lib/utils/content-library";

import type { SortDirection, SortField } from "./content-list-view";

export const DEFAULT_TOOLBAR: ToolbarFilters = {
  type: "all",
  status: "all",
  platform: "all",
  dateRange: "all",
  sort: "updated-desc",
};

export function hasActiveFilters(
  search: string,
  sidebar: SidebarFilterId,
  toolbar: ToolbarFilters,
): boolean {
  return (
    search.trim().length > 0 ||
    sidebar !== "all" ||
    toolbar.type !== "all" ||
    toolbar.status !== "all" ||
    toolbar.platform !== "all" ||
    toolbar.dateRange !== "all"
  );
}

export function listSortToOption(field: SortField, direction: SortDirection): string {
  if (direction === "none") return "updated-desc";
  const suffix = direction === "ascending" ? "asc" : "desc";
  return `${field}-${suffix}`;
}
