import type { PlatformId } from "@/lib/domain/platform";

export type AnalyticsDateRange = "today" | "7d" | "30d" | "90d" | "custom";

export type AnalyticsPost = {
  readonly id: string;
  readonly title: string;
  readonly platform: PlatformId;
  readonly contentType: "article" | "video" | "carousel" | "thread";
  readonly reach: number;
  readonly likes: number;
  readonly comments: number;
  readonly shares: number;
  readonly ctr: number;
  readonly engagementRate: number;
  readonly publishedAt: string;
};

export type AnalyticsInsight = {
  readonly id: string;
  readonly category: "recommendation" | "opportunity" | "publishing" | "summary";
  readonly title: string;
  readonly description: string;
  readonly priority: "high" | "medium" | "low";
};

export type AnalyticsSummary = {
  readonly totalPosts: number;
  readonly totalReach: number;
  readonly totalEngagement: number;
  readonly followersGrowth: number;
  readonly scheduledPosts: number;
  readonly aiContentGenerated: number;
};

export type AnalyticsBaseSummary = {
  readonly totalPosts: number;
  readonly totalReach: number;
  readonly totalEngagement: number;
  readonly followersGrowth: number;
  readonly scheduledPosts: number;
  readonly aiContentGenerated: number;
};

export type TrendPoint = {
  readonly date: string;
  readonly posts: number;
  readonly reach: number;
};

export type EngagementByPlatform = {
  readonly platform: PlatformId;
  readonly label: string;
  readonly engagement: number;
};

export type ReachByPlatform = {
  readonly platform: PlatformId;
  readonly label: string;
  readonly reach: number;
  readonly color: string;
};

export type AiUsagePoint = {
  readonly date: string;
  readonly generated: number;
  readonly approved: number;
};

export type PostingTimePoint = {
  readonly hour: string;
  readonly engagement: number;
};

export type ContentTypePerformance = {
  readonly type: string;
  readonly engagement: number;
  readonly posts: number;
};

export type PlatformComparison = {
  readonly platform: PlatformId;
  readonly label: string;
  readonly reach: number;
  readonly engagement: number;
  readonly avgCtr: number;
  readonly posts: number;
};

export type DateRangeOption = {
  readonly value: AnalyticsDateRange;
  readonly label: string;
  readonly factor: number;
};

export type PlatformFilterOption = {
  readonly value: PlatformId | "all";
  readonly label: string;
};
