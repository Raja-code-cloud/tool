import {
  mockAiStudioRepository,
  mockAnalyticsRepository,
  mockContentRepository,
  mockDashboardRepository,
  mockSchedulerRepository,
  mockSettingsRepository,
  mockSocialAccountRepository,
  mockWorkspaceRepository,
} from "@/lib/adapters/mock-repositories";
import { createApiClient, createDisabledApiClient } from "@/lib/api";
import { env } from "@/lib/config/env";
import {
  createAiStudioService,
  createAnalyticsService,
  createContentService,
  createDashboardService,
  createSchedulerService,
  createSettingsService,
  createSocialAccountService,
  createWorkspaceService,
} from "@/lib/services/workspace-services";

export const contentService = createContentService(mockContentRepository);
export const schedulerService = createSchedulerService(mockSchedulerRepository);
export const socialAccountService = createSocialAccountService(mockSocialAccountRepository);
export const aiStudioService = createAiStudioService(mockAiStudioRepository);
export const dashboardService = createDashboardService(mockDashboardRepository);
export const analyticsService = createAnalyticsService(mockAnalyticsRepository);
export const settingsService = createSettingsService(mockSettingsRepository);
export const workspaceService = createWorkspaceService(mockWorkspaceRepository);

/** Reserved for HTTP repository adapters once NEXT_PUBLIC_API_BASE_URL is configured. */
export const apiClient = env.NEXT_PUBLIC_API_BASE_URL
  ? createApiClient({ baseUrl: env.NEXT_PUBLIC_API_BASE_URL })
  : createDisabledApiClient();
