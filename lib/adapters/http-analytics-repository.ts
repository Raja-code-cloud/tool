import type {
  AnalyticsDashboardDto,
  AnalyticsDashboardQuery,
  AnalyticsListEnvelope,
  AnalyticsPlatformsQuery,
  AnalyticsPostsQuery,
  AnalyticsSuccessEnvelope,
  PlatformAnalyticsDto,
  PostAnalyticsDto,
} from "@/lib/api/analytics-types";
import type { ApiClient } from "@/lib/api/client";
import { getWorkspaceId } from "@/lib/auth/workspace-store";
import { ApiError } from "@/lib/api/errors";

export type AnalyticsPostsPage = {
  readonly items: readonly PostAnalyticsDto[];
  readonly nextCursor: string | null;
  readonly hasMore: boolean;
  readonly limit: number;
};

export type HttpAnalyticsRepository = {
  getDashboard(query: AnalyticsDashboardQuery): Promise<AnalyticsDashboardDto>;
  listPlatforms(query: AnalyticsPlatformsQuery): Promise<readonly PlatformAnalyticsDto[]>;
  listPosts(query: AnalyticsPostsQuery): Promise<AnalyticsPostsPage>;
  getPost(contentId: string, query: Omit<AnalyticsPostsQuery, "cursor" | "limit" | "sort">): Promise<PostAnalyticsDto>;
};

function buildQuery(params: Record<string, string | number | readonly string[] | undefined>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined) return;
    if (Array.isArray(value)) {
      value.forEach((entry) => search.append(key, entry));
      return;
    }
    search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : "";
}

function workspaceHeaders(): Record<string, string> {
  const workspaceId = getWorkspaceId();
  if (!workspaceId) {
    throw new ApiError(
      "Workspace context is required for analytics requests.",
      "validation_error",
      422,
    );
  }
  return { "X-Workspace-ID": workspaceId };
}

export function createHttpAnalyticsRepository(client: ApiClient): HttpAnalyticsRepository {
  return {
    async getDashboard(query) {
      const response = await client.get<AnalyticsSuccessEnvelope<AnalyticsDashboardDto>>(
        `/api/v1/analytics/dashboard${buildQuery({
          periodStart: query.periodStart,
          periodEnd: query.periodEnd,
          timeZone: query.timeZone,
          metric: query.metric,
          platformId: query.platformId,
        })}`,
        { headers: workspaceHeaders() },
      );
      return response.data.data;
    },

    async listPlatforms(query) {
      const response = await client.get<AnalyticsListEnvelope<PlatformAnalyticsDto>>(
        `/api/v1/analytics/platforms${buildQuery({
          periodStart: query.periodStart,
          periodEnd: query.periodEnd,
          platformId: query.platformId,
          metric: query.metric,
          sort: query.sort,
        })}`,
        { headers: workspaceHeaders() },
      );
      return response.data.data;
    },

    async listPosts(query) {
      const response = await client.get<AnalyticsSuccessEnvelope<readonly PostAnalyticsDto[]>>(
        `/api/v1/analytics/posts${buildQuery({
          periodStart: query.periodStart,
          periodEnd: query.periodEnd,
          platformId: query.platformId,
          socialAccountId: query.socialAccountId,
          cursor: query.cursor,
          limit: query.limit,
          sort: query.sort,
        })}`,
        { headers: workspaceHeaders() },
      );
      const page = response.data.meta?.page;
      return {
        items: response.data.data,
        nextCursor: page?.nextCursor ?? null,
        hasMore: page?.hasMore ?? false,
        limit: page?.limit ?? query.limit ?? 25,
      };
    },

    async getPost(contentId, query) {
      const response = await client.get<AnalyticsSuccessEnvelope<PostAnalyticsDto>>(
        `/api/v1/analytics/post/${contentId}${buildQuery({
          periodStart: query.periodStart,
          periodEnd: query.periodEnd,
          platformId: query.platformId,
        })}`,
        { headers: workspaceHeaders() },
      );
      return response.data.data;
    },
  };
}
