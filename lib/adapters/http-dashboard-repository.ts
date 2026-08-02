import type { HttpAnalyticsRepository } from "@/lib/adapters/http-analytics-repository";
import type { ApiClient } from "@/lib/api/client";
import type {
  ActivityItem,
  AgendaEntry,
  DashboardStatData,
  DashboardStorage,
  DashboardSuggestion,
  PlatformHealth,
  RecentContentRow,
} from "@/lib/domain/dashboard";
import type { DashboardRepository, SchedulerRepository } from "@/lib/domain/repositories";
import { fetchDashboardOverview } from "@/lib/dashboard/fetch-overview";

export function createHttpDashboardRepository(deps: {
  readonly client: ApiClient;
  readonly schedulerRepository: SchedulerRepository;
  readonly analyticsRepository: HttpAnalyticsRepository;
}): DashboardRepository {
  let cachedOverview: Promise<Awaited<ReturnType<typeof fetchDashboardOverview>>> | null = null;

  function loadOverview() {
    cachedOverview ??= fetchDashboardOverview(deps).finally(() => {
      cachedOverview = null;
    });
    return cachedOverview;
  }

  return {
    async getStats(): Promise<readonly DashboardStatData[]> {
      return (await loadOverview()).stats;
    },

    async listSuggestions(): Promise<readonly DashboardSuggestion[]> {
      return (await loadOverview()).suggestions;
    },

    async listAgenda(): Promise<readonly AgendaEntry[]> {
      return (await loadOverview()).agenda;
    },

    async listRecentContent(): Promise<readonly RecentContentRow[]> {
      return (await loadOverview()).recentContent;
    },

    async listRecentActivity(): Promise<readonly ActivityItem[]> {
      return (await loadOverview()).recentActivity;
    },

    async listPlatformHealth(): Promise<readonly PlatformHealth[]> {
      return (await loadOverview()).platformHealth;
    },

    async getStorage(): Promise<DashboardStorage> {
      return (await loadOverview()).storage;
    },

    async getHealthSummary(): Promise<string> {
      return (await loadOverview()).healthSummary;
    },

    async loadOverview() {
      return loadOverview();
    },
  };
}
