"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { isApiError } from "@/lib/api/errors";
import type {
  AiUsagePoint,
  AnalyticsDateRange,
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
import {
  analyticsApiService,
  isBackendAnalyticsEnabled,
  mockAnalyticsService,
} from "@/lib/services";
import type { AnalyticsFilters } from "@/lib/services/workspace-services";

export type AnalyticsTableControls = {
  readonly sort: string;
  readonly search: string;
  readonly cursor: string | null;
  readonly limit: number;
};

export type AnalyticsDataState = {
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

const EMPTY_SUMMARY: AnalyticsSummary = {
  totalPosts: 0,
  totalReach: 0,
  totalEngagement: 0,
  followersGrowth: 0,
  scheduledPosts: 0,
  aiContentGenerated: 0,
};

const EMPTY_STATE: AnalyticsDataState = {
  summary: EMPTY_SUMMARY,
  publishingTrend: [],
  engagementByPlatform: [],
  reachByPlatform: [],
  aiUsageTrend: [],
  topPosts: [],
  worstPosts: [],
  platformComparison: [],
  bestPostingTimes: [],
  contentTypePerformance: [],
  insights: [],
  tablePosts: [],
  platformFilterOptions: [],
  pagination: { nextCursor: null, hasMore: false, limit: 25 },
  partial: false,
  warnings: [],
};

function mapApiError(error: unknown): string {
  if (isApiError(error)) {
    if (error.code === "network_error") return "Network error. Check your connection and retry.";
    if (error.status === 401) return "Your session expired. Sign in again to view analytics.";
    if (error.status === 403) return "You do not have permission to view analytics.";
    if (error.status === 404) return "Analytics data was not found for this workspace.";
    if (error.status === 422) return "Invalid analytics filters. Adjust the date range and retry.";
    if (error.status === 429) return "Too many requests. Wait a moment and refresh.";
    if (error.status >= 500) return "Analytics service is temporarily unavailable.";
    return error.message;
  }
  if (error instanceof Error) return error.message;
  return "Unable to load analytics.";
}

function loadMockAnalytics(filters: AnalyticsFilters): AnalyticsDataState {
  const summary = mockAnalyticsService.computeSummary(filters);
  return {
    summary,
    publishingTrend: mockAnalyticsService.getPublishingTrend(filters),
    engagementByPlatform: mockAnalyticsService
      .getEngagementByPlatform(filters)
      .map((item) => ({ platform: "linkedin" as PlatformId, label: item.label, engagement: item.value })),
    reachByPlatform: mockAnalyticsService.getReachByPlatform(filters),
    aiUsageTrend: mockAnalyticsService.getAiUsageTrend(filters),
    topPosts: mockAnalyticsService.getTopPosts(filters),
    worstPosts: mockAnalyticsService.getWorstPosts(filters),
    platformComparison: mockAnalyticsService.getPlatformComparison(filters),
    bestPostingTimes: mockAnalyticsService.getBestPostingTimes(filters).map((item) => ({
      hour: item.label,
      engagement: item.value,
    })),
    contentTypePerformance: mockAnalyticsService.getContentTypePerformance(filters).map((item) => ({
      type: item.label,
      engagement: item.value,
      posts: item.posts,
    })),
    insights: mockAnalyticsService.getInsights(filters),
    tablePosts: [...mockAnalyticsService.filterPosts(filters)].sort((left, right) => right.reach - left.reach),
    platformFilterOptions: mockAnalyticsService.getPlatformFilterOptions(),
    pagination: { nextCursor: null, hasMore: false, limit: 25 },
    partial: false,
    warnings: [],
  };
}

export function useAnalyticsData(
  filters: AnalyticsFilters,
  tableControls: AnalyticsTableControls,
  refreshKey: number,
) {
  const [state, setState] = useState<AnalyticsDataState>(EMPTY_STATE);
  const [isLoading, setIsLoading] = useState(!isBackendAnalyticsEnabled);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!isBackendAnalyticsEnabled) {
      setState(loadMockAnalytics(filters));
      setError(null);
      setIsLoading(false);
      setIsRefreshing(false);
      return;
    }

    setIsRefreshing(true);
    setError(null);
    try {
      const result = await analyticsApiService.loadAnalytics(filters, tableControls);
      setState(result);
    } catch (loadError) {
      setError(mapApiError(loadError));
      setState(EMPTY_STATE);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [filters, tableControls, refreshKey]);

  useEffect(() => {
    void load();
  }, [load]);

  const dateRangeOptions = useMemo(
    () =>
      isBackendAnalyticsEnabled
        ? analyticsApiService.getDateRangeOptions()
        : mockAnalyticsService.getDateRangeOptions(),
    [],
  );

  return {
    ...state,
    isLoading,
    isRefreshing,
    error,
    dateRangeOptions,
    reload: load,
  };
}

export function useAnalyticsFiltersState() {
  const [filters, setFilters] = useState<AnalyticsFilters>({
    dateRange: "30d" as AnalyticsDateRange,
    platform: "all",
  });
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("-reach");
  const [cursor, setCursor] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const patchFilters = (patch: Partial<AnalyticsFilters>) => {
    setFilters((previous) => ({ ...previous, ...patch }));
    setCursor(null);
  };

  const refresh = () => setRefreshKey((previous) => previous + 1);

  return {
    filters,
    search,
    sort,
    cursor,
    refreshKey,
    setSearch,
    setSort,
    setCursor,
    patchFilters,
    refresh,
    setPlatform: (platform: PlatformId | "all") => patchFilters({ platform }),
    setDateRange: (dateRange: AnalyticsDateRange) => patchFilters({ dateRange }),
  };
}
