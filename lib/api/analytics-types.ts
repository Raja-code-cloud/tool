/** Transport DTOs for analytics API endpoints. */

export type MetricValueDto = {
  readonly code: string;
  readonly value: string;
  readonly unit: string;
  readonly isEstimated: boolean;
};

export type AnalyticsDashboardDto = {
  readonly periodStart: string;
  readonly periodEnd: string;
  readonly timeZone: string;
  readonly freshThrough: string;
  readonly methodologyVersion: number;
  readonly metrics: readonly MetricValueDto[];
};

export type PlatformAnalyticsDto = {
  readonly platformId: string;
  readonly platformCode: string;
  readonly accountCount: number;
  readonly freshThrough: string;
  readonly metrics: readonly MetricValueDto[];
};

export type PostAnalyticsDto = {
  readonly contentId: string;
  readonly publicationTargetId?: string | null;
  readonly snapshotAt: string;
  readonly reach?: number | null;
  readonly engagements?: number | null;
  readonly clicks?: number | null;
  readonly conversions?: number | null;
  readonly engagementRate?: string | null;
  readonly metrics: readonly MetricValueDto[];
};

export type AnalyticsSuccessEnvelope<T> = {
  readonly success: true;
  readonly message: string;
  readonly data: T;
  readonly meta?: {
    readonly requestId?: string;
    readonly page?: AnalyticsPageMeta;
    readonly warnings?: readonly string[];
  };
};

export type AnalyticsListEnvelope<T> = {
  readonly success: true;
  readonly message: string;
  readonly data: readonly T[];
  readonly meta?: {
    readonly requestId?: string;
    readonly warnings?: readonly string[];
  };
};

export type AnalyticsPageMeta = {
  readonly nextCursor?: string | null;
  readonly hasMore: boolean;
  readonly limit: number;
};

export type AnalyticsPostsQuery = {
  readonly periodStart: string;
  readonly periodEnd: string;
  readonly platformId?: readonly string[];
  readonly socialAccountId?: readonly string[];
  readonly cursor?: string;
  readonly limit?: number;
  readonly sort?: string;
};

export type AnalyticsDashboardQuery = {
  readonly periodStart: string;
  readonly periodEnd: string;
  readonly timeZone?: string;
  readonly metric?: readonly string[];
  readonly platformId?: readonly string[];
};

export type AnalyticsPlatformsQuery = {
  readonly periodStart: string;
  readonly periodEnd: string;
  readonly platformId?: readonly string[];
  readonly metric?: readonly string[];
  readonly sort?: string;
};
