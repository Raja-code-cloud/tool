export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export type ApiRequestConfig = {
  readonly method?: HttpMethod;
  readonly headers?: Readonly<Record<string, string>>;
  readonly body?: unknown;
  readonly signal?: AbortSignal;
};

export type ApiResponse<T> = {
  readonly data: T;
  readonly status: number;
  readonly headers: Headers;
};

export type PaginatedResponse<T> = {
  readonly items: readonly T[];
  readonly total: number;
  readonly page: number;
  readonly pageSize: number;
  readonly hasMore: boolean;
};

export type ListQueryParams = {
  readonly page?: number;
  readonly pageSize?: number;
  readonly sort?: string;
  readonly search?: string;
};

/** Content API transport shapes (DTOs). Map to domain types in repository adapters. */
export type ContentItemDto = {
  readonly id: string;
  readonly title: string;
  readonly type: string;
  readonly status: string;
  readonly publishing_status: string;
  readonly platforms: readonly string[];
  readonly tags: readonly string[];
  readonly author: string;
  readonly summary: string;
  readonly created_at: string;
  readonly updated_at: string;
  readonly is_favorite: boolean;
  readonly thumbnail_hue: number;
};

export type ScheduledPostDto = {
  readonly id: string;
  readonly title: string;
  readonly platforms: readonly string[];
  readonly scheduled_at: string;
  readonly timezone: string;
  readonly status: string;
  readonly priority: string;
  readonly thumbnail_hue: number;
  readonly ai_version: string;
  readonly approval_status: string;
  readonly queue_order: number;
  readonly has_content: boolean;
};

export type AnalyticsPostDto = {
  readonly id: string;
  readonly title: string;
  readonly platform: string;
  readonly content_type: string;
  readonly reach: number;
  readonly likes: number;
  readonly comments: number;
  readonly shares: number;
  readonly ctr: number;
  readonly engagement_rate: number;
  readonly published_at: string;
};
