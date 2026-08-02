"use client";

import dynamic from "next/dynamic";

import { Dialog, DrawerContent } from "@/components/dialogs";
import { Spinner } from "@/components/feedback";
import { PageContainer, Stack } from "@/components/layout";
import { Pagination } from "@/components/navigation";
import type { ToolbarFilters } from "@/lib/utils/content-library";

import { ContentGrid } from "./content-grid";
import { BulkActionBar, ContentLibraryEmptyState } from "./content-library-empty";
import { ContentLibraryHeader } from "./content-library-header";
import { ContentListView } from "./content-list-view";
import { ContentToolbar } from "./content-toolbar";
import { FilterSidebar } from "./filter-sidebar";
import { useContentLibraryState } from "./use-content-library-state";

const ContentPreviewPanel = dynamic(() =>
  import("./content-preview-panel").then((module) => module.ContentPreviewPanel),
);

export function ContentLibraryView(): React.JSX.Element {
  const state = useContentLibraryState();
  return (
    <PageContainer>
      <Stack gap="lg">
        <ContentLibraryHeader />
        <div className="desktop:grid-cols-[14rem_minmax(0,1fr)] desktop:items-start grid gap-6">
          <aside className="desktop:block hidden">
            <FilterSidebar
              activeFilter={state.sidebarFilter}
              onFilterChange={state.setSidebarFilter}
              counts={state.sidebarCounts}
            />
          </aside>
          <Stack gap="md">
            <ContentToolbar
              search={state.search}
              onSearchChange={state.setSearch}
              typeFilter={state.toolbar.type}
              onTypeFilterChange={(value) =>
                state.updateToolbar({ type: value as ToolbarFilters["type"] })
              }
              statusFilter={state.toolbar.status}
              onStatusFilterChange={(value) =>
                state.updateToolbar({ status: value as ToolbarFilters["status"] })
              }
              platformFilter={state.toolbar.platform}
              onPlatformFilterChange={(value) => state.updateToolbar({ platform: value })}
              dateFilter={state.toolbar.dateRange}
              onDateFilterChange={(value) => state.updateToolbar({ dateRange: value })}
              sort={state.toolbar.sort}
              onSortChange={(value) => state.updateToolbar({ sort: value })}
              viewMode={state.viewMode}
              onViewModeChange={state.setViewMode}
              onRefresh={state.handleRefresh}
              isRefreshing={state.isRefreshing}
              resultCount={state.filteredItems.length}
              onOpenFilters={() => state.setMobileFiltersOpen(true)}
            />
            {state.isRefreshing ? (
              <div className="grid min-h-48 place-items-center" role="status">
                <Spinner label="Refreshing content library" />
              </div>
            ) : state.filteredItems.length === 0 ? (
              <ContentLibraryEmptyState hasActiveFilters={state.filtersActive} />
            ) : state.viewMode === "grid" ? (
              <ContentGrid
                items={state.pageItems}
                selectedIds={state.selectedIds}
                onToggleSelect={state.toggleSelect}
                onSelect={state.setPreviewItem}
                onToggleFavorite={state.toggleFavorite}
              />
            ) : (
              <ContentListView
                items={state.pageItems}
                selectedIds={state.selectedIds}
                onToggleSelect={state.toggleSelect}
                onToggleSelectAll={state.toggleSelectAll}
                onSelect={state.setPreviewItem}
                sortField={state.listSortField}
                sortDirection={state.listSortDirection}
                onSort={state.handleListSort}
              />
            )}
            {state.filteredItems.length > 0 && (
              <Pagination
                page={state.safePage}
                pageCount={state.pageCount}
                pageSize={state.pageSize}
                total={state.filteredItems.length}
                onPageChange={state.setPage}
              />
            )}
            <BulkActionBar
              selectedCount={state.selectedIds.size}
              onClear={() => state.setSelectedIds(new Set())}
            />
          </Stack>
        </div>
      </Stack>
      {state.previewItem && (
        <ContentPreviewPanel item={state.previewItem} onClose={() => state.setPreviewItem(null)} />
      )}
      <Dialog open={state.mobileFiltersOpen} onOpenChange={state.setMobileFiltersOpen}>
        <DrawerContent
          side="left"
          title="Filters"
          description="Narrow your content library."
          className="max-w-xs"
        >
          <FilterSidebar
            activeFilter={state.sidebarFilter}
            onFilterChange={(filterId) => {
              state.setSidebarFilter(filterId);
              state.setMobileFiltersOpen(false);
            }}
            counts={state.sidebarCounts}
          />
        </DrawerContent>
      </Dialog>
    </PageContainer>
  );
}
