import type {
  AnalyticsDashboardDto,
  MetricValueDto,
  PlatformAnalyticsDto,
  PostAnalyticsDto,
} from "@/lib/api/analytics-types";
import { metricNumber } from "@/lib/analytics/metrics";
import {
  isKnownPlatformCode,
  platformChartColor,
  platformLabel,
} from "@/lib/analytics/platform-colors";
import type {
  AnalyticsBaseSummary,
  AnalyticsInsight,
  AnalyticsPost,
  AnalyticsSummary,
  ContentTypePerformance,
  EngagementByPlatform,
  PlatformComparison,
  PlatformFilterOption,
  PostingTimePoint,
  ReachByPlatform,
  TrendPoint,
} from "@/lib/domain/analytics";
import type { PlatformId } from "@/lib/domain/platform";

function parseEngagementRate(value: string | null | undefined): number {
  if (!value) return 0;
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 0;
  return parsed <= 1 ? parsed * 100 : parsed;
}

function parseCtr(clicks: number | null | undefined, reach: number | null | undefined): number {
  if (!clicks || !reach) return 0;
  return (clicks / reach) * 100;
}

function shortContentTitle(contentId: string): string {
  return `Content ${contentId.slice(0, 8)}`;
}

export function mapDashboardSummary(
  dashboard: AnalyticsDashboardDto,
  postCount: number,
): AnalyticsSummary {
  const metrics = dashboard.metrics;
  return {
    totalPosts: metricNumber(metrics, "totalPosts") ?? postCount,
    totalReach: metricNumber(metrics, "reach") ?? 0,
    totalEngagement: metricNumber(metrics, "engagements") ?? 0,
    followersGrowth: metricNumber(metrics, "followersGrowth") ?? 0,
    scheduledPosts: metricNumber(metrics, "scheduledPosts") ?? 0,
    aiContentGenerated: metricNumber(metrics, "aiContentGenerated") ?? 0,
  };
}

export function mapDashboardBaseSummary(dashboard: AnalyticsDashboardDto): AnalyticsBaseSummary {
  return mapDashboardSummary(dashboard, 0);
}

export function mapPostAnalyticsDto(
  dto: PostAnalyticsDto,
  platform: PlatformId = "linkedin",
): AnalyticsPost {
  const reach = dto.reach ?? 0;
  const likes = metricNumber(dto.metrics, "likes") ?? 0;
  const comments = metricNumber(dto.metrics, "comments") ?? 0;
  const shares = metricNumber(dto.metrics, "shares") ?? 0;
  const clicks = dto.clicks ?? metricNumber(dto.metrics, "clicks") ?? 0;

  return {
    id: dto.contentId,
    title: shortContentTitle(dto.contentId),
    platform,
    contentType: "article",
    reach,
    likes: likes || Math.floor((dto.engagements ?? 0) * 0.6),
    comments: comments || Math.floor((dto.engagements ?? 0) * 0.25),
    shares: shares || Math.floor((dto.engagements ?? 0) * 0.15),
    ctr: parseCtr(clicks, reach),
    engagementRate: parseEngagementRate(dto.engagementRate),
    publishedAt: dto.snapshotAt,
  };
}

export function mapPlatformEngagement(
  platforms: readonly PlatformAnalyticsDto[],
): EngagementByPlatform[] {
  return platforms.flatMap((platform) => {
    if (!isKnownPlatformCode(platform.platformCode)) return [];
    const engagement =
      metricNumber(platform.metrics, "engagements") ??
      sumPlatformEngagement(platform.metrics);
    return [
      {
        platform: platform.platformCode,
        label: platformLabel(platform.platformCode),
        engagement,
      },
    ];
  });
}

export function mapPlatformReach(platforms: readonly PlatformAnalyticsDto[]): ReachByPlatform[] {
  return platforms.flatMap((platform) => {
    if (!isKnownPlatformCode(platform.platformCode)) return [];
    const reach = metricNumber(platform.metrics, "reach") ?? metricNumber(platform.metrics, "impressions") ?? 0;
    return [
      {
        platform: platform.platformCode,
        label: platformLabel(platform.platformCode),
        reach,
        color: platformChartColor(platform.platformCode),
      },
    ];
  });
}

export function mapPlatformComparison(
  platforms: readonly PlatformAnalyticsDto[],
  posts: readonly AnalyticsPost[],
): PlatformComparison[] {
  return platforms.flatMap((platform) => {
    if (!isKnownPlatformCode(platform.platformCode)) return [];
    const reach = metricNumber(platform.metrics, "reach") ?? 0;
    const engagement = metricNumber(platform.metrics, "engagements") ?? sumPlatformEngagement(platform.metrics);
    const clicks = metricNumber(platform.metrics, "clicks") ?? 0;
    const impressions = metricNumber(platform.metrics, "impressions") ?? reach;
    const platformPosts = posts.filter((post) => post.platform === platform.platformCode);

    return [
      {
        platform: platform.platformCode,
        label: platformLabel(platform.platformCode),
        reach,
        engagement,
        avgCtr: impressions > 0 ? (clicks / impressions) * 100 : 0,
        posts: platformPosts.length,
      },
    ];
  });
}

export function mapPlatformFilterOptions(
  platforms: readonly PlatformAnalyticsDto[],
): PlatformFilterOption[] {
  const options: PlatformFilterOption[] = [{ value: "all", label: "All platforms" }];
  platforms.forEach((platform) => {
    if (!isKnownPlatformCode(platform.platformCode)) return;
    options.push({
      value: platform.platformCode,
      label: platformLabel(platform.platformCode),
    });
  });
  return options;
}

export function buildPublishingTrend(posts: readonly AnalyticsPost[]): TrendPoint[] {
  const buckets = new Map<string, { posts: number; reach: number }>();
  posts.forEach((post) => {
    const date = new Date(post.publishedAt);
    const key = date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    const current = buckets.get(key) ?? { posts: 0, reach: 0 };
    buckets.set(key, {
      posts: current.posts + 1,
      reach: current.reach + post.reach,
    });
  });

  return [...buckets.entries()].map(([date, values]) => ({
    date,
    posts: values.posts,
    reach: values.reach,
  }));
}

export function buildBestPostingTimes(posts: readonly AnalyticsPost[]): PostingTimePoint[] {
  const buckets = new Map<number, number>();
  posts.forEach((post) => {
    const hour = new Date(post.publishedAt).getHours();
    const engagement = post.likes + post.comments + post.shares;
    buckets.set(hour, (buckets.get(hour) ?? 0) + engagement);
  });

  return [...buckets.entries()]
    .sort(([left], [right]) => left - right)
    .map(([hour, engagement]) => ({
      hour: formatHourLabel(hour),
      engagement,
    }));
}

export function buildContentTypePerformance(
  posts: readonly AnalyticsPost[],
): ContentTypePerformance[] {
  const buckets = new Map<string, { engagement: number; posts: number }>();
  posts.forEach((post) => {
    const current = buckets.get(post.contentType) ?? { engagement: 0, posts: 0 };
    buckets.set(post.contentType, {
      engagement: current.engagement + post.likes + post.comments + post.shares,
      posts: current.posts + 1,
    });
  });

  return [...buckets.entries()].map(([type, values]) => ({
    type,
    engagement: values.engagement,
    posts: values.posts,
  }));
}

export function buildInsightsFromPlatforms(
  platforms: readonly PlatformAnalyticsDto[],
): AnalyticsInsight[] {
  if (platforms.length === 0) return [];

  const ranked = platforms
    .map((platform) => ({
      platform,
      engagement: metricNumber(platform.metrics, "engagements") ?? 0,
    }))
    .sort((left, right) => right.engagement - left.engagement);

  const top = ranked[0];
  if (!top || top.engagement <= 0 || !isKnownPlatformCode(top.platform.platformCode)) {
    return [];
  }

  return [
    {
      id: `platform-top-${top.platform.platformId}`,
      category: "summary",
      title: `${platformLabel(top.platform.platformCode)} leads engagement`,
      description: `${platformLabel(top.platform.platformCode)} generated the highest engagement in the selected period.`,
      priority: "medium",
    },
  ];
}

function sumPlatformEngagement(metrics: readonly MetricValueDto[]): number {
  return (
    (metricNumber(metrics, "likes") ?? 0) +
    (metricNumber(metrics, "comments") ?? 0) +
    (metricNumber(metrics, "shares") ?? 0)
  );
}

function formatHourLabel(hour: number): string {
  const normalized = hour % 12 || 12;
  const suffix = hour < 12 ? "AM" : "PM";
  return `${normalized} ${suffix}`;
}

export function buildPlatformIdMap(
  platforms: readonly PlatformAnalyticsDto[],
): ReadonlyMap<PlatformId, string> {
  const map = new Map<PlatformId, string>();
  platforms.forEach((platform) => {
    if (isKnownPlatformCode(platform.platformCode)) {
      map.set(platform.platformCode, platform.platformId);
    }
  });
  return map;
}
