import { createHttpAiStudioRepository } from "@/lib/adapters/http-ai-studio-repository";
import { createHttpAnalyticsRepository } from "@/lib/adapters/http-analytics-repository";
import { createHttpAuthRepository } from "@/lib/adapters/http-auth-repository";
import { createMockAuthRepository } from "@/lib/adapters/mock-auth-repository";
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
import { getAccessToken } from "@/lib/auth/token-store";
import { env } from "@/lib/config/env";
import { createAnalyticsApiService } from "@/lib/services/analytics-api-service";
import { createAuthService, type AuthService } from "@/lib/services/auth-service";
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

export const contentService = createContentService(mockContentRepository);
export const schedulerService = createSchedulerService(mockSchedulerRepository);
export const socialAccountService = createSocialAccountService(mockSocialAccountRepository);
export const aiStudioService = createAiStudioService(aiStudioRepository);
export const dashboardService = createDashboardService(mockDashboardRepository);
export const mockAnalyticsService = createAnalyticsService(mockAnalyticsRepository);
export const analyticsService = mockAnalyticsService;

const httpAnalyticsRepository = isBackendAnalyticsEnabled
  ? createHttpAnalyticsRepository(apiClient)
  : null;

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
export const settingsService = createSettingsService(mockSettingsRepository);
export const workspaceService = createWorkspaceService(mockWorkspaceRepository);
