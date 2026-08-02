import type {
  ContentItem,
  ContentStatus,
  ContentType,
  SidebarFilterId,
} from "@/lib/domain/content";

export type ToolbarFilters = {
  readonly type: ContentType | "all";
  readonly status: ContentStatus | "all";
  readonly platform: string;
  readonly dateRange: string;
  readonly sort: string;
};

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

export function filterBySidebar(
  items: readonly ContentItem[],
  filterId: SidebarFilterId,
): readonly ContentItem[] {
  if (filterId === "all") return items;
  if (filterId === "favorites") return items.filter((item) => item.isFavorite);

  const type = SIDEBAR_TYPE_MAP[filterId];
  if (type) return items.filter((item) => item.type === type);

  const status = SIDEBAR_STATUS_MAP[filterId];
  if (status) return items.filter((item) => item.status === status);

  return items;
}

export function filterByToolbar(
  items: readonly ContentItem[],
  filters: ToolbarFilters,
): readonly ContentItem[] {
  let result = items;

  if (filters.type !== "all") {
    result = result.filter((item) => item.type === filters.type);
  }
  if (filters.status !== "all") {
    result = result.filter((item) => item.status === filters.status);
  }
  if (filters.platform !== "all") {
    result = result.filter((item) => item.platforms.includes(filters.platform));
  }
  if (filters.dateRange !== "all") {
    const days =
      filters.dateRange === "7d"
        ? 7
        : filters.dateRange === "30d"
          ? 30
          : filters.dateRange === "90d"
            ? 90
            : null;
    if (days !== null) {
      const cutoff = Date.now() - days * 86_400_000;
      result = result.filter((item) => new Date(item.updatedAt).getTime() >= cutoff);
    }
  }

  return result;
}

export function searchContent(
  items: readonly ContentItem[],
  query: string,
): readonly ContentItem[] {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return items;

  return items.filter((item) => {
    const haystack = [item.title, item.type, item.author, ...item.tags, ...item.platforms]
      .join(" ")
      .toLowerCase();
    return haystack.includes(normalized);
  });
}

export function sortContent(items: readonly ContentItem[], sort: string): readonly ContentItem[] {
  const sorted = [...items];

  switch (sort) {
    case "updated-asc":
      return sorted.sort(
        (a, b) => new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime(),
      );
    case "created-desc":
      return sorted.sort(
        (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
      );
    case "created-asc":
      return sorted.sort(
        (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime(),
      );
    case "title-asc":
      return sorted.sort((a, b) => a.title.localeCompare(b.title));
    case "title-desc":
      return sorted.sort((a, b) => b.title.localeCompare(a.title));
    case "type-asc":
      return sorted.sort((a, b) => a.type.localeCompare(b.type));
    case "type-desc":
      return sorted.sort((a, b) => b.type.localeCompare(a.type));
    case "status-asc":
      return sorted.sort((a, b) => a.status.localeCompare(b.status));
    case "status-desc":
      return sorted.sort((a, b) => b.status.localeCompare(a.status));
    case "author-asc":
      return sorted.sort((a, b) => a.author.localeCompare(b.author));
    case "author-desc":
      return sorted.sort((a, b) => b.author.localeCompare(a.author));
    case "updated-desc":
    default:
      return sorted.sort(
        (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
      );
  }
}

export function paginateItems<T>(
  items: readonly T[],
  page: number,
  pageSize: number,
): readonly T[] {
  const start = (page - 1) * pageSize;
  return items.slice(start, start + pageSize);
}

export function countBySidebarFilter(
  items: readonly ContentItem[],
  filterId: SidebarFilterId,
): number {
  return filterBySidebar(items, filterId).length;
}
