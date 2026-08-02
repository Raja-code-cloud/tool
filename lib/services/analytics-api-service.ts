import type { HttpAnalyticsRepository } from "@/lib/adapters/http-analytics-repository";
import { resolveAnalyticsPeriod } from "@/lib/analytics/date-range";
import {
  buildBestPostingTimes,
  buildContentTypePerformance,
  buildInsightsFromPlatforms,
  buildPlatformIdMap,
  buildPublishingTrend,
  mapDashboardSummary,
  mapPlatformComparison,
  mapPlatformEngagement,
  mapPlatformFilterOptions,
  mapPlatformReach,
  mapPostAnalyticsDto,
} from "@/lib/analytics/mappers";
import { ANALYTICS_DATE_RANGES, ANALYTICS_PLATFORMS } from "@/constants/analytics";
import type {
  AiUsagePoint,
  AnalyticsInsight,
  AnalyticsPost,
  AnalyticsSummary,
  ContentTypePerformance,
  DateRangeOption,
  EngagementByPlatform,
  PlatformComparison,
  PlatformFilterOption,
  PostingTimePoint,
  ReachByPlatform,
  TrendPoint,
} from "@/lib/domain/analytics";
import type { PlatformId } from "@/lib/domain/platform";
import type { AnalyticsFilters } from "@/lib/services/workspace-services";

export type AnalyticsTableState = {
  readonly sort: string;
  readonly search: string;
  readonly cursor: string | null;
  readonly limit: number;
};

export type AnalyticsLoadResult = {
  readonly summary: AnalyticsSummary;
  readonly publishingTrend: readonly TrendPoint[];
  readonly engagementByPlatform: readonly EngagementByPlatform[];
  readonly reachByPlatform: readonly ReachByPlatform[];
  readonly aiUsageTrend: readonly AiUsagePoint[];
  readonly topPosts: readonly AnalyticsPost[];
  readonly worstPosts: readonly AnalyticsPost[];
  readonly platformComparison: readonly PlatformComparison[];
  readonly bestPostingTimes: readonly PostingTimePoint[];
  readonly contentTypePerformance: readonly ContentTypePerformance[];
  readonly insights: readonly AnalyticsInsight[];
  readonly tablePosts: readonly AnalyticsPost[];
  readonly platformFilterOptions: readonly PlatformFilterOption[];
  readonly pagination: {
    readonly nextCursor: string | null;
    readonly hasMore: boolean;
    readonly limit: number;
  };
  readonly partial: boolean;
  readonly warnings: readonly string[];
};

const DEFAULT_TABLE_STATE: AnalyticsTableState = {
  sort: "-reach",
  search: "",
  cursor: null,
  limit: 50,
};

export function getAnalyticsDateRangeOptions(): readonly DateRangeOption[] {
  return ANALYTICS_DATE_RANGES;
}

export function getDefaultPlatformFilterOptions(): readonly PlatformFilterOption[] {
  return ANALYTICS_PLATFORMS;
}

function filterPostsBySearch(posts: readonly AnalyticsPost[], search: string): AnalyticsPost[] {
  const query = search.trim().toLowerCase();
  if (!query) return [...posts];
  return posts.filter(
    (post) =>
      post.title.toLowerCase().includes(query) ||
      post.platform.toLowerCase().includes(query) ||
      post.id.toLowerCase().includes(query),
  );
}

function filterPostsByPlatform(
  posts: readonly AnalyticsPost[],
  platform: PlatformId | "all",
): AnalyticsPost[] {
  if (platform === "all") return [...posts];
  return posts.filter((post) => post.platform === platform);
}

export function createAnalyticsApiService(repository: HttpAnalyticsRepository) {
  return {
    getDateRangeOptions: getAnalyticsDateRangeOptions,
    getDefaultPlatformFilterOptions,

    async loadAnalytics(
      filters: AnalyticsFilters,
      tableState: AnalyticsTableState = DEFAULT_TABLE_STATE,
    ): Promise<AnalyticsLoadResult> {
      const period = resolveAnalyticsPeriod(filters.dateRange);
      const warnings: string[] = [];
      let partial = false;

      const platforms = await repository.listPlatforms({
        periodStart: period.periodStart,
        periodEnd: period.periodEnd,
      });
      const platformIdMap = buildPlatformIdMap(platforms);
      const platformIds =
        filters.platform === "all"
          ? undefined
          : platformIdMap.has(filters.platform)
            ? ([platformIdMap.get(filters.platform)!] as readonly string[])
            : undefined;

      const dashboardQuery = {
        periodStart: period.periodStart,
        periodEnd: period.periodEnd,
        ...(platformIds ? { platformId: platformIds } : {}),
      };

      const postsQuery = {
        periodStart: period.periodStart,
        periodEnd: period.periodEnd,
        limit: tableState.limit,
        sort: tableState.sort,
        ...(platformIds ? { platformId: platformIds } : {}),
        ...(tableState.cursor ? { cursor: tableState.cursor } : {}),
      };

      const [dashboard, postsPage] = await Promise.all([
        repository.getDashboard(dashboardQuery),
        repository.listPosts(postsQuery),
      ]);

      const filteredPlatforms =
        filters.platform === "all"
          ? platforms
          : platforms.filter((platform) => platform.platformCode === filters.platform);

      const defaultPlatform =
        filters.platform === "all"
          ? ("linkedin" as PlatformId)
          : filters.platform;

      const posts = postsPage.items.map((item) => mapPostAnalyticsDto(item, defaultPlatform));
      const filteredPosts = filterPostsBySearch(
        filterPostsByPlatform(posts, filters.platform),
        tableState.search,
      );

      const summary = mapDashboardSummary(dashboard, filteredPosts.length);
      const publishingTrend = buildPublishingTrend(filteredPosts);
      const engagementByPlatform = mapPlatformEngagement(filteredPlatforms);
      const reachByPlatform = mapPlatformReach(filteredPlatforms);
      const platformComparison = mapPlatformComparison(filteredPlatforms, filteredPosts);
      const bestPostingTimes = buildBestPostingTimes(filteredPosts);
      const contentTypePerformance = buildContentTypePerformance(filteredPosts);
      const insights = buildInsightsFromPlatforms(filteredPlatforms);

      if (engagementByPlatform.length === 0 && reachByPlatform.length === 0) {
        partial = true;
        warnings.push("Platform breakdown is unavailable for the selected period.");
      }

      if (filteredPosts.length === 0) {
        partial = true;
        warnings.push("No post analytics matched the selected filters.");
      }

      const sortedByEngagement = [...filteredPosts].sort(
        (left, right) => right.engagementRate - left.engagementRate,
      );

      return {
        summary,
        publishingTrend,
        engagementByPlatform,
        reachByPlatform,
        aiUsageTrend: [],
        topPosts: sortedByEngagement.slice(0, 5),
        worstPosts: [...sortedByEngagement].reverse().slice(0, 5),
        platformComparison,
        bestPostingTimes,
        contentTypePerformance,
        insights,
        tablePosts: [...filteredPosts].sort((left, right) => right.reach - left.reach),
        platformFilterOptions:
          mapPlatformFilterOptions(platforms).length > 1
            ? mapPlatformFilterOptions(platforms)
            : getDefaultPlatformFilterOptions(),
        pagination: {
          nextCursor: postsPage.nextCursor,
          hasMore: postsPage.hasMore,
          limit: postsPage.limit,
        },
        partial,
        warnings,
      };
    },
  };
}

export type AnalyticsApiService = ReturnType<typeof createAnalyticsApiService>;

export function exportAnalyticsCsv(posts: readonly AnalyticsPost[]): string {
  const headers = [
    "Content ID",
    "Title",
    "Platform",
    "Reach",
    "Likes",
    "Comments",
    "Shares",
    "CTR",
    "Engagement Rate",
    "Published At",
  ];
  const rows = posts.map((post) => [
    post.id,
    post.title,
    post.platform,
    String(post.reach),
    String(post.likes),
    String(post.comments),
    String(post.shares),
    String(post.ctr),
    String(post.engagementRate),
    post.publishedAt,
  ]);
  return [headers, ...rows]
    .map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(","))
    .join("\n");
}

export function downloadCsv(filename: string, content: string): void {
  const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
