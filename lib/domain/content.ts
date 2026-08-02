export type ContentType = "article" | "poster" | "video" | "thumbnail";
export type ContentStatus = "draft" | "scheduled" | "published" | "archived";
export type PublishingStatus = "not_started" | "queued" | "live" | "failed";

export type ContentItem = {
  readonly id: string;
  readonly title: string;
  readonly type: ContentType;
  readonly status: ContentStatus;
  readonly publishingStatus: PublishingStatus;
  readonly platforms: readonly string[];
  readonly tags: readonly string[];
  readonly author: string;
  readonly summary: string;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly isFavorite: boolean;
  readonly thumbnailHue: number;
};

export type SidebarFilterId =
  | "all"
  | "articles"
  | "posters"
  | "videos"
  | "thumbnails"
  | "drafts"
  | "scheduled"
  | "published"
  | "archived"
  | "favorites";
