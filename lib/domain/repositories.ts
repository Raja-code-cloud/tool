import type { AiStudioProject, AiSuggestion } from "@/lib/domain/ai-studio";
import type {
  AiStudioGenerationRequest,
  AiStudioGenerationResult,
  AiStudioProviderOption,
  AiStudioSaveDraftRequest,
  AiStudioSaveDraftResult,
} from "@/lib/domain/ai-studio-generation";
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
import type { ContentItem, ContentStatus, ContentType } from "@/lib/domain/content";
import type {
  ActivityItem,
  AgendaEntry,
  DashboardStorage,
  DashboardSuggestion,
  PlatformHealth,
  RecentContentRow,
} from "@/lib/domain/dashboard";
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

export interface AiStudioRepository {
  getProject(): AiStudioProject | Promise<AiStudioProject>;
  listSuggestions(): readonly AiSuggestion[] | Promise<readonly AiSuggestion[]>;
  listProviders(): Promise<readonly AiStudioProviderOption[]>;
  generate(request: AiStudioGenerationRequest): Promise<AiStudioGenerationResult>;
  regenerate(request: AiStudioGenerationRequest): Promise<AiStudioGenerationResult>;
  saveDraft(request: AiStudioSaveDraftRequest): Promise<AiStudioSaveDraftResult>;
  cancelGeneration(): void;
}

export type ContentListParams = {
  readonly cursor?: string;
  readonly limit?: number;
  readonly assetTypes?: readonly ContentType[];
  readonly lifecycleStatuses?: readonly ("draft" | "active" | "archived")[];
  readonly sort?: string;
  readonly query?: string;
  readonly projectId?: string;
};

export type ContentListResult = {
  readonly items: readonly ContentItem[];
  readonly nextCursor: string | null;
  readonly hasMore: boolean;
};

export type ContentUpdateInput = {
  readonly title: string;
  readonly summary?: string | null;
  readonly bodyText?: string | null;
  readonly metadata?: Readonly<Record<string, unknown>>;
  readonly lifecycleStatus?: ContentStatus;
};

export interface ContentRepository {
  list(params?: ContentListParams): Promise<ContentListResult>;
  getById(id: string): Promise<ContentItem>;
  delete(id: string, version: number): Promise<void>;
  archive(id: string, version: number): Promise<ContentItem>;
  update(id: string, version: number, input: ContentUpdateInput): Promise<ContentItem>;
}

export interface SchedulerRepository {
  listPosts(filters?: ListSchedulesFilters): Promise<readonly ScheduledPost[]>;
  listNotifications(): readonly SchedulerNotification[];
  getSchedule(id: string): Promise<ScheduledPost>;
  createSchedule(input: CreateScheduleInput): Promise<ScheduledPost>;
  updateSchedule(id: string, version: number, input: UpdateScheduleInput): Promise<ScheduledPost>;
  cancelSchedule(id: string, version: number): Promise<ScheduledPost>;
  dispatchPublication(
    publicationId: string,
    version: number,
    targetIds?: readonly string[],
  ): Promise<void>;
  cancelPublication(publicationId: string, version: number): Promise<void>;
  retryPublication(
    publicationId: string,
    version: number,
    targetIds?: readonly string[],
  ): Promise<void>;
}

export type CreateScheduleInput = {
  readonly publicationTargetId: string;
  readonly requestedLocalAt: string;
  readonly timeZone: string;
  readonly priority?: "low" | "normal" | "high";
  readonly ambiguityPolicy?: "reject" | "earlier" | "later";
  readonly fold?: 0 | 1;
};

export type UpdateScheduleInput = {
  readonly requestedLocalAt?: string;
  readonly timeZone?: string;
  readonly priority?: "low" | "normal" | "high";
  readonly ambiguityPolicy?: "reject" | "earlier" | "later";
  readonly fold?: 0 | 1;
  readonly state?: "scheduled" | "paused";
};

export type ListSchedulesFilters = {
  readonly cursor?: string;
  readonly limit?: number;
  readonly state?: readonly string[];
  readonly priority?: readonly string[];
  readonly scheduledAfter?: string;
  readonly scheduledBefore?: string;
  readonly sort?: string;
};

export interface SocialAccountRepository {
  listAccounts(): readonly SocialAccount[];
  listActivity(): readonly ActivityEvent[];
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
