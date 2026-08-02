import type { ContentStatus, ContentType, SidebarFilterId } from "@/lib/domain/content";

export const CONTENT_TYPES: readonly { value: ContentType | "all"; label: string }[] = [
  { value: "all", label: "All types" },
  { value: "article", label: "Articles" },
  { value: "poster", label: "Posters" },
  { value: "video", label: "Videos" },
  { value: "thumbnail", label: "Thumbnails" },
];
export const CONTENT_STATUSES: readonly { value: ContentStatus | "all"; label: string }[] = [
  { value: "all", label: "All statuses" },
  { value: "draft", label: "Draft" },
  { value: "scheduled", label: "Scheduled" },
  { value: "published", label: "Published" },
  { value: "archived", label: "Archived" },
];
export const CONTENT_PLATFORMS = [
  { value: "all", label: "All platforms" },
  { value: "LinkedIn", label: "LinkedIn" },
  { value: "Instagram", label: "Instagram" },
  { value: "YouTube", label: "YouTube" },
  { value: "X", label: "X" },
  { value: "Blog", label: "Blog" },
  { value: "TikTok", label: "TikTok" },
] as const;
export const DATE_FILTERS = [
  { value: "all", label: "All time", days: null },
  { value: "7d", label: "Last 7 days", days: 7 },
  { value: "30d", label: "Last 30 days", days: 30 },
  { value: "90d", label: "Last 90 days", days: 90 },
] as const;
export const SORT_OPTIONS = [
  { value: "updated-desc", label: "Recently updated" },
  { value: "updated-asc", label: "Oldest updated" },
  { value: "created-desc", label: "Recently created" },
  { value: "created-asc", label: "Oldest created" },
  { value: "title-asc", label: "Title A–Z" },
  { value: "title-desc", label: "Title Z–A" },
] as const;
export const SIDEBAR_FILTERS: readonly { id: SidebarFilterId; label: string }[] = [
  { id: "all", label: "All content" },
  { id: "articles", label: "Articles" },
  { id: "posters", label: "Posters" },
  { id: "videos", label: "Videos" },
  { id: "thumbnails", label: "Thumbnails" },
  { id: "drafts", label: "Drafts" },
  { id: "scheduled", label: "Scheduled" },
  { id: "published", label: "Published" },
  { id: "archived", label: "Archived" },
  { id: "favorites", label: "Favorites" },
];
export const PAGE_SIZE_GRID = 9;
export const PAGE_SIZE_LIST = 10;
