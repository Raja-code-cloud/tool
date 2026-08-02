"use client";

import * as React from "react";

import { PAGE_SIZE_GRID, PAGE_SIZE_LIST, SIDEBAR_FILTERS } from "@/lib/config/content-library";
import type { ContentItem, SidebarFilterId } from "@/lib/domain/content";
import { contentService } from "@/lib/services";
import {
  countBySidebarFilter,
  filterBySidebar,
  filterByToolbar,
  paginateItems,
  searchContent,
  sortContent,
  type ToolbarFilters,
} from "@/lib/utils/content-library";

import { DEFAULT_TOOLBAR, hasActiveFilters, listSortToOption } from "./content-library-state";
import type { SortDirection, SortField } from "./content-list-view";
import type { ViewMode } from "./content-toolbar";

export function useContentLibraryState() {
  const [items, setItems] = React.useState<readonly ContentItem[]>(() => contentService.list());
  const [search, setSearch] = React.useState("");
  const [sidebarFilter, setSidebarFilter] = React.useState<SidebarFilterId>("all");
  const [toolbar, setToolbar] = React.useState<ToolbarFilters>(DEFAULT_TOOLBAR);
  const [viewMode, setViewMode] = React.useState<ViewMode>("grid");
  const [selectedIds, setSelectedIds] = React.useState<ReadonlySet<string>>(new Set());
  const [previewItem, setPreviewItem] = React.useState<ContentItem | null>(null);
  const [page, setPage] = React.useState(1);
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [mobileFiltersOpen, setMobileFiltersOpen] = React.useState(false);
  const [listSortField, setListSortField] = React.useState<SortField>("updated");
  const [listSortDirection, setListSortDirection] = React.useState<SortDirection>("descending");
  const sidebarCounts = React.useMemo(() => {
    const counts = {} as Record<SidebarFilterId, number>;
    for (const filter of SIDEBAR_FILTERS)
      counts[filter.id] = countBySidebarFilter(items, filter.id);
    return counts;
  }, [items]);
  const filteredItems = React.useMemo(
    () =>
      sortContent(
        searchContent(filterByToolbar(filterBySidebar(items, sidebarFilter), toolbar), search),
        toolbar.sort,
      ),
    [items, search, sidebarFilter, toolbar],
  );
  const pageSize = viewMode === "grid" ? PAGE_SIZE_GRID : PAGE_SIZE_LIST;
  const pageCount = Math.max(1, Math.ceil(filteredItems.length / pageSize));
  const safePage = Math.min(page, pageCount);
  const pageItems = paginateItems(filteredItems, safePage, pageSize);
  React.useEffect(() => {
    if (page > pageCount) setPage(pageCount);
  }, [page, pageCount]);
  React.useEffect(() => {
    setPage(1);
  }, [search, sidebarFilter, toolbar, viewMode]);
  const updateToolbar = (patch: Partial<ToolbarFilters>): void =>
    setToolbar((current) => ({ ...current, ...patch }));
  const toggleSelect = (id: string, checked: boolean): void =>
    setSelectedIds((current) => {
      const next = new Set(current);
      if (checked) next.add(id);
      else next.delete(id);
      return next;
    });
  const toggleSelectAll = (checked: boolean): void =>
    setSelectedIds(checked ? new Set(pageItems.map((item) => item.id)) : new Set());
  const toggleFavorite = (id: string): void =>
    setItems((current) =>
      current.map((item) => (item.id === id ? { ...item, isFavorite: !item.isFavorite } : item)),
    );
  const handleRefresh = (): void => {
    setIsRefreshing(true);
    window.setTimeout(() => setIsRefreshing(false), 600);
  };
  const handleListSort = (field: SortField): void => {
    const direction: SortDirection =
      listSortField !== field
        ? "ascending"
        : listSortDirection === "ascending"
          ? "descending"
          : "ascending";
    setListSortField(field);
    setListSortDirection(direction);
    updateToolbar({ sort: listSortToOption(field, direction) });
  };
  return {
    search,
    setSearch,
    sidebarFilter,
    setSidebarFilter,
    toolbar,
    updateToolbar,
    viewMode,
    setViewMode,
    selectedIds,
    setSelectedIds,
    previewItem,
    setPreviewItem,
    isRefreshing,
    mobileFiltersOpen,
    setMobileFiltersOpen,
    listSortField,
    listSortDirection,
    sidebarCounts,
    filteredItems,
    pageSize,
    pageCount,
    safePage,
    pageItems,
    setPage,
    toggleSelect,
    toggleSelectAll,
    toggleFavorite,
    handleRefresh,
    handleListSort,
    filtersActive: hasActiveFilters(search, sidebarFilter, toolbar),
  };
}
