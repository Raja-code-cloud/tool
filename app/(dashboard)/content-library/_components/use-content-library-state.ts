"use client";

import * as React from "react";

import { PAGE_SIZE_GRID, PAGE_SIZE_LIST, SIDEBAR_FILTERS } from "@/lib/config/content-library";
import type { ContentItem, ContentStatus, ContentType, SidebarFilterId } from "@/lib/domain/content";
import type { ContentListParams } from "@/lib/domain/repositories";
import { getApiErrorMessage, isApiError } from "@/lib/api/errors";
import { mapStatusToLifecycle } from "@/lib/content/mappers";
import { contentService, isBackendAuthEnabled } from "@/lib/services";
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

const SIDEBAR_TYPE_MAP: Partial<Record<SidebarFilterId, ContentType>> = {
  articles: "article",
  posters: "poster",
  videos: "video",
  thumbnails: "thumbnail",
};

const SIDEBAR_STATUS_MAP: Partial<Record<SidebarFilterId, ContentStatus>> = {
  drafts: "draft",
  scheduled: "scheduled",
  published: "published",
  archived: "archived",
};

function buildListParams(
  search: string,
  sidebarFilter: SidebarFilterId,
  toolbar: ToolbarFilters,
): ContentListParams {
  const params: ContentListParams = {
    limit: 100,
    sort: toolbar.sort.includes("updated") ? "-updatedAt" : "-createdAt",
  };

  if (search.trim().length >= 2 && isBackendAuthEnabled) {
    params.query = search.trim();
  }

  const sidebarType = SIDEBAR_TYPE_MAP[sidebarFilter];
  if (sidebarType) params.assetTypes = [sidebarType];
  else if (toolbar.type !== "all") params.assetTypes = [toolbar.type];

  const sidebarStatus = SIDEBAR_STATUS_MAP[sidebarFilter];
  const status = sidebarStatus ?? (toolbar.status !== "all" ? toolbar.status : null);
  if (status && status !== "scheduled") {
    const lifecycle = mapStatusToLifecycle(status);
    if (lifecycle) params.lifecycleStatuses = [lifecycle];
  }

  return params;
}

export function useContentLibraryState() {
  const [items, setItems] = React.useState<readonly ContentItem[]>([]);
  const [search, setSearch] = React.useState("");
  const [sidebarFilter, setSidebarFilter] = React.useState<SidebarFilterId>("all");
  const [toolbar, setToolbar] = React.useState<ToolbarFilters>(DEFAULT_TOOLBAR);
  const [viewMode, setViewMode] = React.useState<ViewMode>("grid");
  const [selectedIds, setSelectedIds] = React.useState<ReadonlySet<string>>(new Set());
  const [previewItem, setPreviewItem] = React.useState<ContentItem | null>(null);
  const [page, setPage] = React.useState(1);
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(true);
  const [loadError, setLoadError] = React.useState<string | null>(null);
  const [mobileFiltersOpen, setMobileFiltersOpen] = React.useState(false);
  const [listSortField, setListSortField] = React.useState<SortField>("updated");
  const [listSortDirection, setListSortDirection] = React.useState<SortDirection>("descending");

  const fetchItems = React.useCallback(async () => {
    setLoadError(null);
    try {
      const result = await contentService.list(buildListParams(search, sidebarFilter, toolbar));
      setItems(result.items);
    } catch (error) {
      setLoadError(getApiErrorMessage(error));
      if (!isApiError(error) || error.code !== "network_error") {
        setItems([]);
      }
    }
  }, [search, sidebarFilter, toolbar]);

  React.useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    void fetchItems().finally(() => {
      if (!cancelled) setIsLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [fetchItems]);

  const sidebarCounts = React.useMemo(() => {
    const counts = {} as Record<SidebarFilterId, number>;
    for (const filter of SIDEBAR_FILTERS)
      counts[filter.id] = countBySidebarFilter(items, filter.id);
    return counts;
  }, [items]);

  const filteredItems = React.useMemo(() => {
    const useClientSearch = !isBackendAuthEnabled || search.trim().length < 2;
    let result = filterBySidebar(items, sidebarFilter);
    result = filterByToolbar(result, toolbar);
    if (useClientSearch && search.trim()) {
      result = searchContent(result, search);
    }
    return sortContent(result, toolbar.sort);
  }, [items, search, sidebarFilter, toolbar]);

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
    void fetchItems().finally(() => setIsRefreshing(false));
  };

  const handleDelete = async (item: ContentItem): Promise<void> => {
    await contentService.delete(item.id, item.version);
    setItems((current) => current.filter((entry) => entry.id !== item.id));
    setSelectedIds((current) => {
      const next = new Set(current);
      next.delete(item.id);
      return next;
    });
    if (previewItem?.id === item.id) setPreviewItem(null);
  };

  const handleArchive = async (item: ContentItem): Promise<void> => {
    const archived = await contentService.archive(item.id, item.version);
    setItems((current) => current.map((entry) => (entry.id === item.id ? archived : entry)));
  };

  const handleBulkDelete = async (): Promise<void> => {
    const selected = items.filter((item) => selectedIds.has(item.id));
    await Promise.all(selected.map((item) => contentService.delete(item.id, item.version)));
    setItems((current) => current.filter((item) => !selectedIds.has(item.id)));
    setSelectedIds(new Set());
  };

  const handleBulkArchive = async (): Promise<void> => {
    const selected = items.filter((item) => selectedIds.has(item.id));
    const archived = await Promise.all(
      selected.map((item) => contentService.archive(item.id, item.version)),
    );
    const archivedById = new Map(archived.map((item) => [item.id, item]));
    setItems((current) =>
      current.map((item) => archivedById.get(item.id) ?? item),
    );
    setSelectedIds(new Set());
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
    isLoading,
    loadError,
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
    handleDelete,
    handleArchive,
    handleBulkDelete,
    handleBulkArchive,
    handleListSort,
    filtersActive: hasActiveFilters(search, sidebarFilter, toolbar),
  };
}
