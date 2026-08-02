import type { AiStudioProject, AiSuggestion } from "@/lib/domain/ai-studio";
import type {
  AiUsagePoint,
  AnalyticsBaseSummary,
  AnalyticsInsight,
  AnalyticsPost,
  ContentTypePerformance,
  DateRangeOption,
  EngagementByPlatform,
  PlatformComparison,
  PlatformFilterOption,
  PostingTimePoint,
  ReachByPlatform,
  TrendPoint,
} from "@/lib/domain/analytics";
import type { ContentItem } from "@/lib/domain/content";
import type {
  ActivityItem,
  AgendaEntry,
  DashboardStorage,
  DashboardSuggestion,
  PlatformHealth,
  RecentContentRow,
} from "@/lib/domain/dashboard";
import type { PlatformId } from "@/lib/domain/platform";
import type { ScheduledPost, SchedulerNotification } from "@/lib/domain/scheduler";
import type {
  AiProvider,
  ApiKeyRecord,
  NotificationPreference,
  ProfileDefaults,
  PublishingDefaults,
  SessionRecord,
  StorageUsage,
} from "@/lib/domain/settings";
import type { ActivityEvent, SocialAccount } from "@/lib/domain/social-account";
import type { WorkspaceInfo, WorkspaceUser } from "@/lib/domain/workspace";
import type {
  AuthProvider,
  AuthSession,
  AuthTokens,
  AuthorizationFlow,
  LoginCredentials,
} from "@/lib/domain/auth";

export type GeneratedPlatformContent = {
  readonly content: string;
  readonly hashtags: readonly string[];
  readonly cta: string;
};

export interface ContentRepository {
  list(): readonly ContentItem[];
}

export interface SchedulerRepository {
  listPosts(): readonly ScheduledPost[];
  listNotifications(): readonly SchedulerNotification[];
}

export interface SocialAccountRepository {
  listAccounts(): readonly SocialAccount[];
  listActivity(): readonly ActivityEvent[];
}

export interface AiStudioRepository {
  getPlatformContent(platform: PlatformId): GeneratedPlatformContent;
  getProject(): AiStudioProject;
  listSuggestions(): readonly AiSuggestion[];
}

export interface DashboardRepository {
  listSuggestions(): readonly DashboardSuggestion[];
  listAgenda(): readonly AgendaEntry[];
  listRecentContent(): readonly RecentContentRow[];
  listRecentActivity(): readonly ActivityItem[];
  listPlatformHealth(): readonly PlatformHealth[];
  getStorage(): DashboardStorage;
  getHealthSummary(): string;
}

export interface AnalyticsRepository {
  listPosts(): readonly AnalyticsPost[];
  listInsights(): readonly AnalyticsInsight[];
  getBaseSummary(): AnalyticsBaseSummary;
  getPublishingTrend(): readonly TrendPoint[];
  getEngagementByPlatform(): readonly EngagementByPlatform[];
  getReachByPlatform(): readonly ReachByPlatform[];
  getAiUsageTrend(): readonly AiUsagePoint[];
  getBestPostingTimes(): readonly PostingTimePoint[];
  getContentTypePerformance(): readonly ContentTypePerformance[];
  getPlatformComparison(): readonly PlatformComparison[];
  getDateRangeOptions(): readonly DateRangeOption[];
  getPlatformFilterOptions(): readonly PlatformFilterOption[];
}

export interface SettingsRepository {
  getProfileDefaults(): ProfileDefaults;
  listNotificationPreferences(): readonly NotificationPreference[];
  listAiProviders(): readonly AiProvider[];
  getStorageUsage(): StorageUsage;
  getPublishingDefaults(): PublishingDefaults;
  listActiveSessions(): readonly SessionRecord[];
  listApiKeys(): readonly ApiKeyRecord[];
}

export interface AuthRepository {
  listProviders(): Promise<readonly AuthProvider[]>;
  beginAuthorization(providerCode: string, redirectUri: string): Promise<AuthorizationFlow>;
  login(credentials: LoginCredentials): Promise<AuthSession>;
  logout(): Promise<void>;
  refreshAccessToken(): Promise<AuthTokens>;
  getCurrentSession(): Promise<AuthSession>;
}

export interface WorkspaceRepository {
  getWorkspace(): WorkspaceInfo;
  getCurrentUser(): WorkspaceUser;
  getUnreadNotificationCount(): number;
}
