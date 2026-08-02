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
import type { PlatformId } from "@/lib/domain/platform";
import type {
  AiStudioRepository,
  AnalyticsRepository,
  ContentRepository,
  DashboardRepository,
  GeneratedPlatformContent,
  SchedulerRepository,
  SettingsRepository,
  SocialAccountRepository,
  WorkspaceRepository,
} from "@/lib/domain/repositories";

export const mockContentRepository: ContentRepository = {
  list: () => CONTENT_LIBRARY_ITEMS,
};

export const mockSchedulerRepository: SchedulerRepository = {
  listPosts: () => SCHEDULED_POSTS,
  listNotifications: () => INITIAL_NOTIFICATIONS,
};

export const mockSocialAccountRepository: SocialAccountRepository = {
  listAccounts: () => [...SOCIAL_ACCOUNTS, ...COMING_SOON_ACCOUNTS],
  listActivity: () => ACTIVITY_EVENTS,
};

export const mockAiStudioRepository: AiStudioRepository = {
  getPlatformContent(platform: PlatformId): GeneratedPlatformContent {
    return MOCK_PLATFORM_CONTENT[platform];
  },
  getProject: () => AI_STUDIO_PROJECT,
  listSuggestions: () => AI_SUGGESTIONS,
};

export const mockDashboardRepository: DashboardRepository = {
  listSuggestions: () => DASHBOARD_SUGGESTIONS,
  listAgenda: () => TODAY_AGENDA,
  listRecentContent: () => RECENT_CONTENT,
  listRecentActivity: () => RECENT_ACTIVITY,
  listPlatformHealth: () => PLATFORM_HEALTH,
  getStorage: () => DASHBOARD_STORAGE,
  getHealthSummary: () => WORKSPACE_HEALTH_SUMMARY,
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
  getProfileDefaults: () => PROFILE_DEFAULTS,
  listNotificationPreferences: () => NOTIFICATION_PREFERENCES,
  listAiProviders: () => AI_PROVIDERS,
  getStorageUsage: () => STORAGE_USAGE,
  getPublishingDefaults: () => PUBLISHING_DEFAULTS,
  listActiveSessions: () => ACTIVE_SESSIONS,
  listApiKeys: () => API_KEYS,
};

export const mockWorkspaceRepository: WorkspaceRepository = {
  getWorkspace: () => WORKSPACE,
  getCurrentUser: () => CURRENT_USER,
  getUnreadNotificationCount: () => UNREAD_NOTIFICATION_COUNT,
};
