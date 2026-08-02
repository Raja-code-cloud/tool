import type { HttpAnalyticsRepository } from "@/lib/adapters/http-analytics-repository";
import { resolveAnalyticsPeriod } from "@/lib/analytics/date-range";
import type { AssetDto, PagedSuccessEnvelope } from "@/lib/api/asset-types";
import type { ApiClient } from "@/lib/api/client";
import type {
  HealthDto,
  ListSuccessEnvelope,
  NotificationDto,
  ProbeDto,
  ProviderHealthDto,
  PublicationHistoryItemDto,
  QueueStatusDto,
  SystemStatusDto,
} from "@/lib/api/dashboard-types";
import type { ScheduleCalendarDto } from "@/lib/api/scheduler-types";
import {
  buildHealthSummary,
  computeStorageFromAssets,
  countPage,
  mapAssetToRecentContentRow,
  mapDashboardStats,
  mapNotificationToActivity,
  mapNotificationToSuggestion,
  mapProviderToPlatformHealth,
  mapPublicationHistoryToActivity,
  mapScheduleToAgendaEntry,
} from "@/lib/dashboard/mappers";
import type {
  ActivityItem,
  AgendaEntry,
  DashboardStatData,
  DashboardStorage,
  DashboardSuggestion,
  PlatformHealth,
  RecentContentRow,
} from "@/lib/domain/dashboard";
import type { SchedulerRepository } from "@/lib/domain/repositories";
import { toUtcRangeEnd, toUtcRangeStart } from "@/lib/scheduler/mappers";

export type DashboardOverview = {
  readonly stats: readonly DashboardStatData[];
  readonly suggestions: readonly DashboardSuggestion[];
  readonly agenda: readonly AgendaEntry[];
  readonly recentContent: readonly RecentContentRow[];
  readonly recentActivity: readonly ActivityItem[];
  readonly platformHealth: readonly PlatformHealth[];
  readonly storage: DashboardStorage;
  readonly healthSummary: string;
  readonly partial: boolean;
  readonly warnings: readonly string[];
};

type Settled<T> = PromiseSettledResult<T>;

function fulfilled<T>(result: Settled<T>, fallback: T): T {
  return result.status === "fulfilled" ? result.value : fallback;
}

function rejectionWarning(result: Settled<unknown>, label: string): string | null {
  if (result.status === "rejected") {
    const reason = result.reason;
    const message = reason instanceof Error ? reason.message : String(reason);
    return `${label} unavailable: ${message}`;
  }
  return null;
}

async function fetchAssetsPage(
  client: ApiClient,
  query: Record<string, string | readonly string[] | undefined>,
): Promise<{ items: readonly AssetDto[]; hasMore: boolean }> {
  const search = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value === undefined) return;
    if (Array.isArray(value)) {
      value.forEach((entry) => search.append(key, entry));
      return;
    }
    search.set(key, value);
  });
  const path = `/api/v1/assets?${search.toString()}`;
  const response = await client.get<PagedSuccessEnvelope<AssetDto>>(path);
  return {
    items: response.data.data,
    hasMore: response.data.meta?.page?.hasMore ?? false,
  };
}

async function fetchNotifications(
  client: ApiClient,
  limit = 25,
): Promise<readonly NotificationDto[]> {
  const response = await client.get<PagedSuccessEnvelope<NotificationDto>>(
    `/api/v1/notifications?limit=${limit}&sort=-updatedAt`,
  );
  return response.data.data;
}

async function fetchPublicationHistory(
  client: ApiClient,
  limit = 10,
): Promise<readonly PublicationHistoryItemDto[]> {
  const response = await client.get<PagedSuccessEnvelope<PublicationHistoryItemDto>>(
    `/api/v1/publish/history?limit=${limit}&sort=-occurredAt`,
  );
  return response.data.data;
}

async function fetchSocialProviders(client: ApiClient): Promise<readonly ProviderHealthDto[]> {
  const response = await client.get<ListSuccessEnvelope<ProviderHealthDto>>(
    "/api/v1/admin/providers?providerType=social",
  );
  return response.data.data;
}

async function fetchQueueStatus(client: ApiClient): Promise<readonly QueueStatusDto[]> {
  const response = await client.get<ListSuccessEnvelope<QueueStatusDto>>("/api/v1/admin/queues");
  return response.data.data;
}

async function fetchSystemStatus(client: ApiClient): Promise<SystemStatusDto> {
  const response = await client.get<{ success: true; data: SystemStatusDto }>(
    "/api/v1/admin/system",
  );
  return response.data.data;
}

async function fetchReadiness(client: ApiClient): Promise<boolean> {
  const response = await client.get<{ success: true; data: ProbeDto }>("/health/ready");
  return response.data.data.status === "ready";
}

async function fetchTodaySchedules(client: ApiClient): Promise<readonly ScheduleCalendarDto[]> {
  const now = new Date();
  const search = new URLSearchParams({
    scheduledAfter: toUtcRangeStart(now),
    scheduledBefore: toUtcRangeEnd(now),
    sort: "scheduledFor",
    limit: "25",
  });
  const response = await client.get<PagedSuccessEnvelope<ScheduleCalendarDto>>(
    `/api/v1/schedule?${search.toString()}`,
  );
  return response.data.data;
}

async function fetchHealth(client: ApiClient): Promise<HealthDto> {
  const response = await client.get<{ success: true; data: HealthDto }>("/health");
  return response.data.data;
}

export async function fetchDashboardOverview(deps: {
  readonly client: ApiClient;
  readonly schedulerRepository: SchedulerRepository;
  readonly analyticsRepository: HttpAnalyticsRepository;
}): Promise<DashboardOverview> {
  const warnings: string[] = [];
  const period = resolveAnalyticsPeriod("30d");

  const results = await Promise.allSettled([
    fetchAssetsPage(deps.client, { limit: "100", sort: "-updatedAt" }),
    fetchAssetsPage(deps.client, { limit: "100", sort: "-updatedAt", lifecycleStatus: ["draft"] }),
    fetchAssetsPage(deps.client, { limit: "100", sort: "-updatedAt", lifecycleStatus: ["active"] }),
    deps.schedulerRepository.listPosts({ state: ["scheduled", "paused", "draft"], limit: 100 }),
    deps.schedulerRepository.listPosts({ state: ["failed"], limit: 100 }),
    fetchTodaySchedules(deps.client),
    deps.analyticsRepository.getDashboard({
      periodStart: period.periodStart,
      periodEnd: period.periodEnd,
    }),
    fetchNotifications(deps.client),
    fetchPublicationHistory(deps.client),
    fetchSocialProviders(deps.client),
    fetchQueueStatus(deps.client),
    fetchSystemStatus(deps.client),
    fetchReadiness(deps.client),
    fetchHealth(deps.client),
    fetchAssetsPage(deps.client, { limit: "5", sort: "-updatedAt" }),
  ]);

  const [
    allAssetsResult,
    draftAssetsResult,
    activeAssetsResult,
    scheduledResult,
    failedSchedulesResult,
    todayAgendaResult,
    analyticsResult,
    notificationsResult,
    historyResult,
    providersResult,
    queuesResult,
    systemResult,
    readinessResult,
    healthResult,
    recentContentResult,
  ] = results;

  [
    ["Asset totals", allAssetsResult],
    ["Draft assets", draftAssetsResult],
    ["Published assets", activeAssetsResult],
    ["Scheduled posts", scheduledResult],
    ["Failed schedules", failedSchedulesResult],
    ["Today's agenda", todayAgendaResult],
    ["Analytics dashboard", analyticsResult],
    ["Notifications", notificationsResult],
    ["Publication history", historyResult],
    ["Platform providers", providersResult],
    ["Queue status", queuesResult],
    ["System status", systemResult],
    ["Readiness probe", readinessResult],
    ["Health probe", healthResult],
    ["Recent content", recentContentResult],
  ].forEach(([label, result]) => {
    const warning = rejectionWarning(result as Settled<unknown>, label as string);
    if (warning) warnings.push(warning);
  });

  const allAssets = fulfilled(allAssetsResult, { items: [], hasMore: false });
  const draftAssets = fulfilled(draftAssetsResult, { items: [], hasMore: false });
  const activeAssets = fulfilled(activeAssetsResult, { items: [], hasMore: false });
  const scheduledPosts = fulfilled(scheduledResult, []);
  const failedSchedules = fulfilled(failedSchedulesResult, []);
  const todaySchedules = fulfilled(todayAgendaResult, [] as readonly ScheduleCalendarDto[]);
  const analyticsDashboard = fulfilled(analyticsResult, null);
  const notifications = fulfilled(notificationsResult, []);
  const publicationHistory = fulfilled(historyResult, []);
  const providers = fulfilled(providersResult, []);
  const queues = fulfilled(queuesResult, []);
  const systemStatus = fulfilled(systemResult, null);
  const ready = fulfilled(readinessResult, false);
  const recentAssets = fulfilled(recentContentResult, { items: [], hasMore: false });

  const failedAssets = allAssets.items.filter(
    (asset) => asset.media?.scanStatus === "failed" || asset.media?.scanStatus === "infected",
  );

  const stats = mapDashboardStats({
    totalContent: countPage(allAssets.items, allAssets.hasMore),
    draftContent: countPage(draftAssets.items, draftAssets.hasMore),
    publishedContent: countPage(activeAssets.items, activeAssets.hasMore),
    scheduledContent: countPage(scheduledPosts, scheduledPosts.length >= 100),
    failedContent: countPage(
      [...failedSchedules, ...failedAssets],
      failedSchedules.length >= 100 || allAssets.hasMore,
    ),
    analyticsDashboard,
    todayScheduledCount: todaySchedules.length,
  });

  const agenda = todaySchedules.map(mapScheduleToAgendaEntry);

  const recentContent = recentAssets.items.map((asset) => mapAssetToRecentContentRow(asset));

  const activityFromHistory = publicationHistory.map(mapPublicationHistoryToActivity);
  const activityFromNotifications = notifications.map(mapNotificationToActivity);
  const recentActivity = [...activityFromHistory, ...activityFromNotifications]
    .sort((left, right) => Date.parse(right.occurredAt) - Date.parse(left.occurredAt))
    .slice(0, 8);

  const suggestions = notifications
    .map(mapNotificationToSuggestion)
    .filter((item): item is DashboardSuggestion => item !== null)
    .slice(0, 6);

  const platformHealth = providers.map(mapProviderToPlatformHealth);
  const storage = computeStorageFromAssets(allAssets.items);
  const healthSummary = buildHealthSummary({
    ready,
    system: systemStatus,
    providers,
    queues,
  });

  const partial =
    stats.some((stat) => stat.comparison.includes("partial count")) ||
    warnings.length > 0 ||
    allAssets.hasMore;

  if (partial) {
    warnings.push("Some dashboard sections returned partial data.");
  }

  if (suggestions.length === 0 && notifications.length > 0) {
    warnings.push(
      "AI suggestions are derived from notifications until a dedicated endpoint is available.",
    );
  }

  if (activityFromHistory.length === 0 && historyResult.status === "rejected") {
    warnings.push("Recent activity uses notifications because publication history is unavailable.");
  }

  void healthResult;

  return {
    stats,
    suggestions,
    agenda,
    recentContent,
    recentActivity,
    platformHealth,
    storage,
    healthSummary,
    partial,
    warnings,
  };
}
