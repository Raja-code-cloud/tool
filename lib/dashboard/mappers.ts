import type { AssetDto } from "@/lib/api/asset-types";
import type {
  NotificationDto,
  ProviderHealthDto,
  PublicationHistoryItemDto,
  QueueStatusDto,
  SystemStatusDto,
} from "@/lib/api/dashboard-types";
import type { ScheduleCalendarDto } from "@/lib/api/scheduler-types";
import { platformLabel, isKnownPlatformCode } from "@/lib/analytics/platform-colors";
import { metricNumber } from "@/lib/analytics/metrics";
import type { AnalyticsDashboardDto } from "@/lib/api/analytics-types";
import type {
  ActivityItem,
  AgendaEntry,
  DashboardStorage,
  DashboardSuggestion,
  PlatformHealth,
  RecentContentRow,
} from "@/lib/domain/dashboard";
import type { DashboardStatData } from "@/lib/domain/dashboard";
import { mapScheduleStateToStatus } from "@/lib/scheduler/mappers";

export type ContentCountResult = {
  readonly count: number;
  readonly partial: boolean;
};

export type DashboardSummaryInput = {
  readonly totalContent: ContentCountResult;
  readonly draftContent: ContentCountResult;
  readonly publishedContent: ContentCountResult;
  readonly scheduledContent: ContentCountResult;
  readonly failedContent: ContentCountResult;
  readonly analyticsDashboard?: AnalyticsDashboardDto | null;
  readonly todayScheduledCount?: number;
};

function formatCount(value: number, partial: boolean): string {
  if (partial && value >= 100) return `${value}+`;
  return String(value);
}

function partialLabel(partial: boolean): string {
  return partial ? " (partial count)" : "";
}

export function mapDashboardStats(input: DashboardSummaryInput): readonly DashboardStatData[] {
  const publishedFromAnalytics = input.analyticsDashboard
    ? metricNumber(input.analyticsDashboard.metrics, "totalPosts")
    : undefined;
  const scheduledFromAnalytics = input.analyticsDashboard
    ? metricNumber(input.analyticsDashboard.metrics, "scheduledPosts")
    : undefined;

  const publishedCount = Math.max(
    input.publishedContent.count,
    publishedFromAnalytics ?? 0,
  );
  const scheduledCount = Math.max(
    input.scheduledContent.count,
    scheduledFromAnalytics ?? 0,
  );

  const partial =
    input.totalContent.partial ||
    input.draftContent.partial ||
    input.publishedContent.partial ||
    input.scheduledContent.partial ||
    input.failedContent.partial;

  const todayCount = input.todayScheduledCount ?? 0;

  return [
    {
      id: "total-content",
      label: "Total content",
      value: formatCount(input.totalContent.count, input.totalContent.partial),
      comparison: `Across workspace${partialLabel(input.totalContent.partial)}`,
      trend: input.totalContent.count > 0 ? "Active library" : "Empty",
      trendDirection: "neutral",
    },
    {
      id: "scheduled-content",
      label: "Scheduled content",
      value: formatCount(scheduledCount, input.scheduledContent.partial),
      comparison:
        todayCount > 0
          ? `${todayCount} publishing today`
          : `Queued for publishing${partialLabel(input.scheduledContent.partial)}`,
      trend: scheduledCount > 0 ? `${scheduledCount} queued` : "None queued",
      trendDirection: scheduledCount > 0 ? "up" : "neutral",
    },
    {
      id: "published-content",
      label: "Published content",
      value: formatCount(publishedCount, input.publishedContent.partial),
      comparison: `Live assets${partialLabel(input.publishedContent.partial)}`,
      trend: publishedCount > 0 ? "In circulation" : "None yet",
      trendDirection: publishedCount > 0 ? "up" : "neutral",
    },
    {
      id: "failed-content",
      label: "Failed content",
      value: formatCount(input.failedContent.count, input.failedContent.partial),
      comparison: `Needs attention${partialLabel(input.failedContent.partial)}`,
      trend: input.failedContent.count > 0 ? "Action required" : "All clear",
      trendDirection: input.failedContent.count > 0 ? "neutral" : "up",
      variant: input.failedContent.count > 0 ? "warning" : "default",
    },
    {
      id: "draft-content",
      label: "Draft content",
      value: formatCount(input.draftContent.count, input.draftContent.partial),
      comparison: `Work in progress${partialLabel(input.draftContent.partial)}`,
      trend: input.draftContent.count > 0 ? `${input.draftContent.count} drafts` : "None",
      trendDirection: "neutral",
    },
  ];
}

function mapAssetType(type: AssetDto["assetType"]): string {
  switch (type) {
    case "article":
      return "Article";
    case "video":
      return "Video";
    case "poster":
      return "Image";
    case "thumbnail":
      return "Thumbnail";
    default: {
      const _exhaustive: never = type;
      return _exhaustive;
    }
  }
}

function mapAssetStatus(asset: AssetDto): RecentContentRow["status"] {
  if (asset.media?.scanStatus === "failed" || asset.media?.scanStatus === "infected") {
    return "failed";
  }
  switch (asset.lifecycleStatus) {
    case "draft":
      return "draft";
    case "active":
      return "published";
    case "archived":
      return "draft";
    default: {
      const _exhaustive: never = asset.lifecycleStatus;
      return _exhaustive;
    }
  }
}

function extractPlatforms(metadata: Readonly<Record<string, unknown>> | undefined): readonly string[] {
  if (!metadata) return [];
  const platforms = metadata.platforms;
  if (Array.isArray(platforms)) {
    return platforms.filter((value): value is string => typeof value === "string");
  }
  return [];
}

export function mapAssetToRecentContentRow(
  asset: AssetDto,
  ownerLabel = "Workspace",
): RecentContentRow {
  const platforms = extractPlatforms(undefined);
  return {
    id: asset.id,
    title: asset.title,
    type: mapAssetType(asset.assetType),
    variants: Math.max(platforms.length, 1),
    platforms: platforms.length > 0 ? platforms : ["Workspace"],
    status: mapAssetStatus(asset),
    owner: ownerLabel,
    updatedAt: asset.updatedAt,
  };
}

function mapAgendaStatus(
  state: ScheduleCalendarDto["state"],
  publicationStatus: ScheduleCalendarDto["publicationStatus"],
): AgendaEntry["status"] {
  const scheduleStatus = mapScheduleStateToStatus(state, publicationStatus);
  if (scheduleStatus === "published") return "published";
  if (scheduleStatus === "failed") return "failed";
  return "queued";
}

function formatLocalTime(iso: string, timeZone: string): string {
  try {
    return new Intl.DateTimeFormat("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
      timeZone,
    }).format(new Date(iso));
  } catch {
    const date = new Date(iso);
    return `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
  }
}

export function mapScheduleToAgendaEntry(schedule: ScheduleCalendarDto): AgendaEntry {
  const platformCode = schedule.platformCode.toLowerCase();
  const platform = isKnownPlatformCode(platformCode)
    ? platformLabel(platformCode)
    : schedule.platformCode;

  return {
    id: schedule.id,
    time: formatLocalTime(schedule.scheduledFor, schedule.timeZone),
    title: schedule.publicationTitle,
    platform,
    status: mapAgendaStatus(schedule.state, schedule.publicationStatus),
  };
}

export function mapNotificationToActivity(notification: NotificationDto): ActivityItem {
  return {
    id: notification.id,
    actor: notification.severity === "error" ? "System" : "Workspace",
    action: notification.typeCode.replaceAll("_", " "),
    target: notification.title,
    occurredAt: notification.updatedAt,
  };
}

export function mapPublicationHistoryToActivity(item: PublicationHistoryItemDto): ActivityItem {
  return {
    id: item.id,
    actor: "Publishing",
    action: item.toState.replaceAll("_", " "),
    target: `Publication ${item.publicationId.slice(0, 8)}`,
    occurredAt: item.occurredAt,
  };
}

const SUGGESTION_TYPE_CODES = new Set([
  "ai_suggestion",
  "content_recommendation",
  "calendar_gap",
  "token_expiry",
  "reauth_required",
]);

const SUGGESTION_SEVERITIES = new Set<NotificationDto["severity"]>(["warning", "error"]);

export function mapNotificationToSuggestion(notification: NotificationDto): DashboardSuggestion | null {
  const isSuggestion =
    SUGGESTION_TYPE_CODES.has(notification.typeCode) ||
    notification.typeCode.includes("suggestion") ||
    notification.typeCode.includes("recommend");

  if (!isSuggestion && !SUGGESTION_SEVERITIES.has(notification.severity)) {
    return null;
  }

  const priority: DashboardSuggestion["priority"] =
    notification.severity === "error"
      ? "high"
      : notification.severity === "warning"
        ? "medium"
        : "low";

  const href =
    notification.resourceType === "asset"
      ? "/content-library"
      : notification.resourceType === "schedule"
        ? "/scheduler"
        : notification.typeCode.includes("token") || notification.typeCode.includes("reauth")
          ? "/social-accounts"
          : "/ai-studio";

  return {
    id: notification.id,
    title: notification.title,
    reason: notification.body,
    priority,
    actionLabel: "Review",
    href,
  };
}

export function mapProviderToPlatformHealth(provider: ProviderHealthDto): PlatformHealth {
  const status: PlatformHealth["status"] =
    provider.status === "enabled"
      ? "healthy"
      : provider.status === "degraded"
        ? "warning"
        : "error";

  return {
    id: provider.code,
    name: provider.name,
    status,
    detail: provider.message ?? (status === "healthy" ? "Publishing normally" : "Needs attention"),
  };
}

export function computeStorageFromAssets(assets: readonly AssetDto[]): DashboardStorage {
  const usedBytes = assets.reduce((total, asset) => total + (asset.media?.byteSize ?? 0), 0);
  const totalBytes = Math.max(usedBytes, 1_099_511_627_776);
  return {
    usedBytes,
    totalBytes,
    label: "Media library",
  };
}

export function buildHealthSummary(input: {
  readonly ready: boolean;
  readonly system: SystemStatusDto | null;
  readonly providers: readonly ProviderHealthDto[];
  readonly queues: readonly QueueStatusDto[];
}): string {
  if (!input.ready) {
    return "Some services are unavailable · check connectivity";
  }

  if (input.system?.status === "degraded") {
    return "System degraded · review platform health";
  }

  const unhealthyProviders = input.providers.filter((provider) => provider.status !== "enabled");
  const queueIssues = input.queues.filter(
    (queue) => queue.failed > 0 || queue.deadLettered > 0,
  );

  if (unhealthyProviders.length > 0) {
    const label = unhealthyProviders.length === 1 ? "account needs" : "accounts need";
    return `All systems operational · ${unhealthyProviders.length} ${label} attention`;
  }

  if (queueIssues.length > 0) {
    return "Publishing queues have failed jobs · review queue health";
  }

  return "All systems operational";
}

export function countPage<T>(items: readonly T[], hasMore: boolean): ContentCountResult {
  return {
    count: items.length,
    partial: hasMore,
  };
}
