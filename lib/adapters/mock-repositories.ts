import { AI_STUDIO_PROJECT, AI_SUGGESTIONS, MOCK_PLATFORM_CONTENT } from "@/constants/ai-studio";
import {
  AI_USAGE_TREND,
  ANALYTICS_BASE_SUMMARY,
  ANALYTICS_DATE_RANGES,
  ANALYTICS_INSIGHTS,
  ANALYTICS_PLATFORMS,
  ANALYTICS_POSTS,
  BEST_POSTING_TIMES,
  CONTENT_TYPE_PERFORMANCE,
  ENGAGEMENT_BY_PLATFORM,
  PLATFORM_COMPARISON,
  PUBLISHING_TREND,
  REACH_BY_PLATFORM,
} from "@/constants/analytics";
import { CONTENT_LIBRARY_ITEMS } from "@/constants/content-library";
import {
  DASHBOARD_STATS,
  DASHBOARD_STORAGE,
  AI_SUGGESTIONS as DASHBOARD_SUGGESTIONS,
  PLATFORM_HEALTH,
  RECENT_ACTIVITY,
  RECENT_CONTENT,
  TODAY_AGENDA,
  WORKSPACE_HEALTH_SUMMARY,
} from "@/constants/dashboard";
import { INITIAL_NOTIFICATIONS, SCHEDULED_POSTS } from "@/constants/scheduler";
import {
  ACTIVE_SESSIONS,
  AI_PROVIDERS,
  API_KEYS,
  NOTIFICATION_PREFERENCES,
  PROFILE_DEFAULTS,
  PUBLISHING_DEFAULTS,
  STORAGE_USAGE,
} from "@/constants/settings";
import {
  ACTIVITY_EVENTS,
  COMING_SOON_ACCOUNTS,
  SOCIAL_ACCOUNTS,
} from "@/constants/social-accounts";
import { CURRENT_USER, UNREAD_NOTIFICATION_COUNT, WORKSPACE } from "@/constants/workspace";
import { createMockSocialAccountRepository } from "@/lib/adapters/http-social-account-repository";
import { createMockContentRepository } from "@/lib/adapters/http-content-repository";
import { createMockSchedulerRepository } from "@/lib/adapters/http-scheduler-repository";
import type {
  AiStudioRepository,
  AnalyticsRepository,
  ContentRepository,
  DashboardRepository,
  SettingsRepository,
  SocialAccountRepository,
  SocialAccountUpdateInput,
  WorkspaceRepository,
} from "@/lib/domain/repositories";
import { applyExpand, applyShorten, applyToneTransform } from "@/lib/utils/ai-studio";

export const mockContentRepository: ContentRepository =
  createMockContentRepository(CONTENT_LIBRARY_ITEMS);

export const mockSchedulerRepository = createMockSchedulerRepository(
  SCHEDULED_POSTS,
  INITIAL_NOTIFICATIONS,
);

export const mockSocialAccountRepository = createMockSocialAccountRepository(
  [...SOCIAL_ACCOUNTS, ...COMING_SOON_ACCOUNTS],
  ACTIVITY_EVENTS,
);

export const mockAiStudioRepository: AiStudioRepository = {
  getProject: () => AI_STUDIO_PROJECT,
  listSuggestions: () => AI_SUGGESTIONS,

  async listProviders() {
    return [
      {
        id: "mock-model",
        code: "mock",
        name: "Mock provider",
        status: "enabled",
        modelId: "mock-model",
      },
    ];
  },

  async generate(request) {
    const mock = MOCK_PLATFORM_CONTENT[request.platform];
    let content = applyToneTransform(mock.content, request.tone);
    if (request.length === "short") content = applyShorten(content, 0.55);
    if (request.length === "long") content = applyExpand(content);

    return {
      content,
      hashtags: request.generateHashtags ? mock.hashtags : [],
      cta: request.generateCta ? mock.cta : "",
      operationId: `mock-op-${Date.now()}`,
      contentId: AI_STUDIO_PROJECT.id,
      contentVersion: 1,
    };
  },

  async regenerate(request) {
    return mockAiStudioRepository.generate(request);
  },

  async saveDraft() {
    return { savedAt: new Date().toISOString(), contentVersion: 1 };
  },

  cancelGeneration(): void {
    // Mock mode relies on AbortSignal in the caller.
  },
};

export const mockDashboardRepository: DashboardRepository = {
  async getStats() {
    return DASHBOARD_STATS.map(({ icon: _icon, ...stat }) => stat);
  },
  async listSuggestions() {
    return DASHBOARD_SUGGESTIONS;
  },
  async listAgenda() {
    return TODAY_AGENDA;
  },
  async listRecentContent() {
    return RECENT_CONTENT;
  },
  async listRecentActivity() {
    return RECENT_ACTIVITY;
  },
  async listPlatformHealth() {
    return PLATFORM_HEALTH;
  },
  async getStorage() {
    return DASHBOARD_STORAGE;
  },
  async getHealthSummary() {
    return WORKSPACE_HEALTH_SUMMARY;
  },
  async loadOverview() {
    return {
      stats: await mockDashboardRepository.getStats(),
      suggestions: await mockDashboardRepository.listSuggestions(),
      agenda: await mockDashboardRepository.listAgenda(),
      recentContent: await mockDashboardRepository.listRecentContent(),
      recentActivity: await mockDashboardRepository.listRecentActivity(),
      platformHealth: await mockDashboardRepository.listPlatformHealth(),
      storage: await mockDashboardRepository.getStorage(),
      healthSummary: await mockDashboardRepository.getHealthSummary(),
      partial: false,
      warnings: [],
    };
  },
};

export const mockAnalyticsRepository: AnalyticsRepository = {
  listPosts: () => ANALYTICS_POSTS,
  listInsights: () => ANALYTICS_INSIGHTS,
  getBaseSummary: () => ANALYTICS_BASE_SUMMARY,
  getPublishingTrend: () => PUBLISHING_TREND,
  getEngagementByPlatform: () => ENGAGEMENT_BY_PLATFORM,
  getReachByPlatform: () => REACH_BY_PLATFORM,
  getAiUsageTrend: () => AI_USAGE_TREND,
  getBestPostingTimes: () => BEST_POSTING_TIMES,
  getContentTypePerformance: () => CONTENT_TYPE_PERFORMANCE,
  getPlatformComparison: () => PLATFORM_COMPARISON,
  getDateRangeOptions: () => ANALYTICS_DATE_RANGES,
  getPlatformFilterOptions: () => ANALYTICS_PLATFORMS,
};

export const mockSettingsRepository: SettingsRepository = {
  getProfile: () => ({
    id: "mock-user",
    version: 1,
    ...PROFILE_DEFAULTS,
    avatarUrl: null,
  }),
  listNotificationPreferences: () => NOTIFICATION_PREFERENCES,
  listAiProviders: () => AI_PROVIDERS,
  getStorageUsage: () => STORAGE_USAGE,
  getPublishingDefaults: () => PUBLISHING_DEFAULTS,
  listActiveSessions: () => ACTIVE_SESSIONS,
  listApiKeys: () => API_KEYS,
  getUnreadNotificationCount: () => UNREAD_NOTIFICATION_COUNT,
};

export const mockWorkspaceRepository: WorkspaceRepository = {
  getWorkspace: () => WORKSPACE,
  getCurrentUser: () => CURRENT_USER,
  getUnreadNotificationCount: () => UNREAD_NOTIFICATION_COUNT,
};
