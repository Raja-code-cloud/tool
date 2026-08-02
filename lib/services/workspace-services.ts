import type { AnalyticsDateRange, AnalyticsInsight, AnalyticsPost } from "@/lib/domain/analytics";
import type { PlatformId } from "@/lib/domain/platform";
import type {
  AiStudioRepository,
  AnalyticsRepository,
  ContentRepository,
  DashboardRepository,
  SchedulerRepository,
  SettingsRepository,
  SocialAccountRepository,
  WorkspaceRepository,
} from "@/lib/domain/repositories";

export type AnalyticsFilters = {
  dateRange: AnalyticsDateRange;
  platform: PlatformId | "all";
};

function rangeFactor(repository: AnalyticsRepository, range: AnalyticsDateRange): number {
  return repository.getDateRangeOptions().find((item) => item.value === range)?.factor ?? 1;
}

function scale(value: number, factor: number): number {
  return Math.round(value * factor);
}

function filterPosts(posts: readonly AnalyticsPost[], filters: AnalyticsFilters): AnalyticsPost[] {
  let result = [...posts];
  if (filters.platform !== "all") {
    result = result.filter((post) => post.platform === filters.platform);
  }
  return result;
}

function scaleTrendData<T extends Record<string, number | string>>(
  data: readonly T[],
  factor: number,
  numericKeys: readonly (keyof T)[],
): T[] {
  return data.map((point) => {
    const next = { ...point };
    numericKeys.forEach((key) => {
      const value = point[key];
      if (typeof value === "number") {
        (next as Record<string, number | string>)[key as string] = scale(value, factor);
      }
    });
    return next;
  });
}

export function createContentService(repository: ContentRepository) {
  return {
    list: (params?: import("@/lib/domain/repositories").ContentListParams) =>
      repository.list(params),
    getById: (id: string) => repository.getById(id),
    delete: (id: string, version: number) => repository.delete(id, version),
    archive: (id: string, version: number) => repository.archive(id, version),
    update: (
      id: string,
      version: number,
      input: import("@/lib/domain/repositories").ContentUpdateInput,
    ) => repository.update(id, version, input),
  };
}

export function createSchedulerService(repository: SchedulerRepository) {
  return {
    listPosts: () => repository.listPosts(),
    listNotifications: () => repository.listNotifications(),
  };
}

export function createSocialAccountService(repository: SocialAccountRepository) {
  return {
    listAccounts: () => repository.listAccounts(),
    listActivity: () => repository.listActivity(),
  };
}

export function createAiStudioService(repository: AiStudioRepository) {
  return {
    getProject: () => Promise.resolve(repository.getProject()),
    listSuggestions: () => Promise.resolve(repository.listSuggestions()),
    listProviders: () => repository.listProviders(),
    generate: (request: Parameters<AiStudioRepository["generate"]>[0]) => repository.generate(request),
    regenerate: (request: Parameters<AiStudioRepository["regenerate"]>[0]) =>
      repository.regenerate(request),
    saveDraft: (request: Parameters<AiStudioRepository["saveDraft"]>[0]) =>
      repository.saveDraft(request),
    cancelGeneration: () => repository.cancelGeneration(),
  };
}

export function createDashboardService(repository: DashboardRepository) {
  return {
    listSuggestions: () => repository.listSuggestions(),
    listAgenda: () => repository.listAgenda(),
    listRecentContent: () => repository.listRecentContent(),
    listRecentActivity: () => repository.listRecentActivity(),
    listPlatformHealth: () => repository.listPlatformHealth(),
    getStorage: () => repository.getStorage(),
    getHealthSummary: () => repository.getHealthSummary(),
  };
}

export function createAnalyticsService(repository: AnalyticsRepository) {
  return {
    listPosts: () => repository.listPosts(),
    getDateRangeOptions: () => repository.getDateRangeOptions(),
    getPlatformFilterOptions: () => repository.getPlatformFilterOptions(),

    filterPosts(filters: AnalyticsFilters): AnalyticsPost[] {
      const posts = repository.listPosts();
      let result = filterPosts(posts, filters);
      const factor = rangeFactor(repository, filters.dateRange);
      if (factor < 1) {
        const keepCount = Math.max(1, Math.ceil(result.length * factor));
        result = result.slice(0, keepCount);
      }
      return result;
    },

    computeSummary(filters: AnalyticsFilters) {
      const factor = rangeFactor(repository, filters.dateRange);
      const posts = this.filterPosts(filters);
      const base = repository.getBaseSummary();
      const reach =
        posts.reduce((sum, post) => sum + post.reach, 0) || scale(base.totalReach, factor);
      const engagement =
        posts.reduce((sum, post) => sum + post.likes + post.comments + post.shares, 0) ||
        scale(base.totalEngagement, factor);

      return {
        totalPosts: posts.length || scale(base.totalPosts, factor),
        totalReach: reach,
        totalEngagement: engagement,
        followersGrowth: scale(base.followersGrowth, factor),
        scheduledPosts: scale(base.scheduledPosts, Math.max(factor * 0.5, 0.04)),
        aiContentGenerated: scale(base.aiContentGenerated, factor),
      };
    },

    getPublishingTrend(filters: AnalyticsFilters) {
      const factor = rangeFactor(repository, filters.dateRange);
      return scaleTrendData(repository.getPublishingTrend(), factor, ["posts", "reach"]);
    },

    getEngagementByPlatform(filters: AnalyticsFilters) {
      const factor = rangeFactor(repository, filters.dateRange);
      let data = repository.getEngagementByPlatform().map((item) => ({
        label: item.label,
        value: scale(item.engagement, factor),
      }));
      if (filters.platform !== "all") {
        data = data.filter((item) =>
          repository
            .getEngagementByPlatform()
            .some((p) => p.label === item.label && p.platform === filters.platform),
        );
      }
      return data;
    },

    getReachByPlatform(filters: AnalyticsFilters) {
      const factor = rangeFactor(repository, filters.dateRange);
      let data = repository.getReachByPlatform().map((item) => ({
        ...item,
        reach: scale(item.reach, factor),
      }));
      if (filters.platform !== "all") {
        data = data.filter((item) => item.platform === filters.platform);
      }
      return data;
    },

    getAiUsageTrend(filters: AnalyticsFilters) {
      const factor = rangeFactor(repository, filters.dateRange);
      return scaleTrendData(repository.getAiUsageTrend(), factor, ["generated", "approved"]);
    },

    getBestPostingTimes(filters: AnalyticsFilters) {
      const factor = rangeFactor(repository, filters.dateRange);
      return repository.getBestPostingTimes().map((item) => ({
        label: item.hour,
        value: scale(item.engagement, factor),
      }));
    },

    getContentTypePerformance(filters: AnalyticsFilters) {
      const factor = rangeFactor(repository, filters.dateRange);
      return repository.getContentTypePerformance().map((item) => ({
        label: item.type,
        value: scale(item.engagement, factor),
        posts: scale(item.posts, factor),
      }));
    },

    getTopPosts(filters: AnalyticsFilters, limit = 5): AnalyticsPost[] {
      return [...this.filterPosts(filters)]
        .sort((a, b) => b.engagementRate - a.engagementRate)
        .slice(0, limit);
    },

    getWorstPosts(filters: AnalyticsFilters, limit = 5): AnalyticsPost[] {
      return [...this.filterPosts(filters)]
        .sort((a, b) => a.engagementRate - b.engagementRate)
        .slice(0, limit);
    },

    getPlatformComparison(filters: AnalyticsFilters) {
      const factor = rangeFactor(repository, filters.dateRange);
      let data = repository.getPlatformComparison().map((item) => ({
        ...item,
        reach: scale(item.reach, factor),
        engagement: scale(item.engagement, factor),
        posts: scale(item.posts, factor),
      }));
      if (filters.platform !== "all") {
        data = data.filter((item) => item.platform === filters.platform);
      }
      return data;
    },

    getInsights(filters: AnalyticsFilters): AnalyticsInsight[] {
      if (filters.platform !== "all") {
        return repository
          .listInsights()
          .filter(
            (insight) =>
              !insight.description.toLowerCase().includes("facebook") ||
              filters.platform === "facebook",
          );
      }
      return [...repository.listInsights()];
    },
  };
}

export function createSettingsService(repository: SettingsRepository) {
  return {
    getProfileDefaults: () => repository.getProfileDefaults(),
    listNotificationPreferences: () => repository.listNotificationPreferences(),
    listAiProviders: () => repository.listAiProviders(),
    getStorageUsage: () => repository.getStorageUsage(),
    getPublishingDefaults: () => repository.getPublishingDefaults(),
    listActiveSessions: () => repository.listActiveSessions(),
    listApiKeys: () => repository.listApiKeys(),
  };
}

export function createWorkspaceService(repository: WorkspaceRepository) {
  return {
    getWorkspace: () => repository.getWorkspace(),
    getCurrentUser: () => repository.getCurrentUser(),
    getUnreadNotificationCount: () => repository.getUnreadNotificationCount(),
  };
}

export type ContentService = ReturnType<typeof createContentService>;
export type SchedulerService = ReturnType<typeof createSchedulerService>;
export type SocialAccountService = ReturnType<typeof createSocialAccountService>;
export type AiStudioService = ReturnType<typeof createAiStudioService>;
export type DashboardService = ReturnType<typeof createDashboardService>;
export type AnalyticsService = ReturnType<typeof createAnalyticsService>;
export type SettingsService = ReturnType<typeof createSettingsService>;
export type WorkspaceService = ReturnType<typeof createWorkspaceService>;
