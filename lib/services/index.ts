import { createHttpSocialAccountRepository } from "@/lib/adapters/http-social-account-repository";
import { createHttpAiStudioRepository } from "@/lib/adapters/http-ai-studio-repository";
import { createHttpDashboardRepository } from "@/lib/adapters/http-dashboard-repository";
import { createHttpSettingsRepository } from "@/lib/adapters/http-settings-repository";
import { createHttpWorkspaceRepository } from "@/lib/adapters/http-workspace-repository";
import { createHttpAnalyticsRepository } from "@/lib/adapters/http-analytics-repository";
import { createHttpAuthRepository } from "@/lib/adapters/http-auth-repository";
import { createHttpContentRepository } from "@/lib/adapters/http-content-repository";
import { createHttpSchedulerRepository, createMockSchedulerRepository } from "@/lib/adapters/http-scheduler-repository";
import { createMockAuthRepository } from "@/lib/adapters/mock-auth-repository";
import {
  mockAiStudioRepository,
  mockAnalyticsRepository,
  mockContentRepository,
  mockDashboardRepository,
  mockSettingsRepository,
  mockSocialAccountRepository,
  mockWorkspaceRepository,
} from "@/lib/adapters/mock-repositories";
import { INITIAL_NOTIFICATIONS, SCHEDULED_POSTS } from "@/constants/scheduler";
import { createApiClient, createDisabledApiClient } from "@/lib/api";
import { getActiveWorkspaceId } from "@/lib/auth/workspace-store";
import { getAccessToken } from "@/lib/auth/token-store";
import { env } from "@/lib/config/env";
import { createAnalyticsApiService } from "@/lib/services/analytics-api-service";
import { createDashboardApiService } from "@/lib/services/dashboard-api-service";
import { createAuthService, type AuthService } from "@/lib/services/auth-service";
import { createUploadRepository, createUploadService } from "@/lib/services/upload-service";
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

export const isBackendAuthEnabled = Boolean(env.NEXT_PUBLIC_API_BASE_URL);
export const isBackendAnalyticsEnabled = isBackendAuthEnabled;
export const isBackendAiStudioEnabled = isBackendAuthEnabled;
export const isBackendSocialAccountsEnabled = isBackendAuthEnabled;
export const isBackendSchedulerEnabled = isBackendAuthEnabled;
export const isBackendSettingsEnabled = isBackendAuthEnabled;
export const isBackendWorkspaceEnabled = isBackendAuthEnabled;
export const isBackendDashboardEnabled = isBackendAuthEnabled;
export { DASHBOARD_POLL_INTERVAL_MS } from "@/lib/services/dashboard-api-service";

let authServiceRef: AuthService | null = null;

async function handleUnauthorized(): Promise<boolean> {
  if (!authServiceRef) return false;
  try {
    await authServiceRef.refreshAccessToken();
    return true;
  } catch {
    authServiceRef.clearSession();
    return false;
  }
}

export const apiClient = isBackendAuthEnabled
  ? createApiClient({
      baseUrl: env.NEXT_PUBLIC_API_BASE_URL!,
      getAccessToken,
      getWorkspaceId: () =>
        getActiveWorkspaceId() ?? env.NEXT_PUBLIC_WORKSPACE_ID ?? null,
      onUnauthorized: handleUnauthorized,
    })
  : createDisabledApiClient();

const authRepository = isBackendAuthEnabled
  ? createHttpAuthRepository(apiClient)
  : createMockAuthRepository();

export const authService: AuthService = createAuthService(authRepository);
authServiceRef = authService;

const aiStudioRepository = isBackendAiStudioEnabled
  ? createHttpAiStudioRepository(apiClient, {
      getModelId: () => env.NEXT_PUBLIC_AI_MODEL_ID ?? null,
    })
  : mockAiStudioRepository;

export const contentService = createContentService(
  isBackendAuthEnabled ? createHttpContentRepository(apiClient) : mockContentRepository,
);

export const uploadService = isBackendAuthEnabled
  ? createUploadService(createUploadRepository(apiClient, env.NEXT_PUBLIC_API_BASE_URL!))
  : null;
const schedulerRepository = isBackendSchedulerEnabled
  ? createHttpSchedulerRepository(apiClient)
  : createMockSchedulerRepository(SCHEDULED_POSTS, INITIAL_NOTIFICATIONS);

export const schedulerService = createSchedulerService(schedulerRepository);

const socialAccountRepository = isBackendSocialAccountsEnabled
  ? createHttpSocialAccountRepository(apiClient)
  : mockSocialAccountRepository;

export const socialAccountService = createSocialAccountService(socialAccountRepository);
export const aiStudioService = createAiStudioService(aiStudioRepository);
const httpAnalyticsRepository = isBackendAnalyticsEnabled
  ? createHttpAnalyticsRepository(apiClient)
  : null;

const dashboardRepository = isBackendDashboardEnabled
  ? createHttpDashboardRepository({
      client: apiClient,
      schedulerRepository,
      analyticsRepository: httpAnalyticsRepository ?? createHttpAnalyticsRepository(apiClient),
    })
  : mockDashboardRepository;

export const dashboardService = createDashboardService(dashboardRepository);
export const dashboardApiService = createDashboardApiService(dashboardRepository);

export const mockAnalyticsService = createAnalyticsService(mockAnalyticsRepository);
export const analyticsService = mockAnalyticsService;

export const analyticsApiService = httpAnalyticsRepository
  ? createAnalyticsApiService(httpAnalyticsRepository)
  : createAnalyticsApiService({
      getDashboard: async () => {
        throw new Error("Analytics API is not configured.");
      },
      listPlatforms: async () => {
        throw new Error("Analytics API is not configured.");
      },
      listPosts: async () => {
        throw new Error("Analytics API is not configured.");
      },
      getPost: async () => {
        throw new Error("Analytics API is not configured.");
      },
    });
const settingsRepository = isBackendSettingsEnabled
  ? createHttpSettingsRepository(apiClient)
  : mockSettingsRepository;

const workspaceRepository = isBackendWorkspaceEnabled
  ? createHttpWorkspaceRepository(apiClient, {
      getProfile: () => settingsRepository.getProfile(),
      getUnreadCount: () =>
        settingsRepository.getUnreadNotificationCount
          ? settingsRepository.getUnreadNotificationCount()
          : Promise.resolve(0),
    })
  : mockWorkspaceRepository;

export const settingsService = createSettingsService(settingsRepository);
export const workspaceService = createWorkspaceService(workspaceRepository);
