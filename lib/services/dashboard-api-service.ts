import { isApiError } from "@/lib/api/errors";
import type { DashboardOverview } from "@/lib/dashboard/fetch-overview";
import type { DashboardRepository } from "@/lib/domain/repositories";

export type DashboardLoadResult = DashboardOverview & {
  readonly offline: boolean;
  readonly error: string | null;
};

function mapDashboardError(error: unknown): string {
  if (isApiError(error)) {
    if (error.code === "network_error") {
      return "Network error. Dashboard is showing cached or empty data.";
    }
    if (error.status === 401) {
      return "Your session expired. Sign in again to view the dashboard.";
    }
    if (error.status === 403) {
      return "You do not have permission to view some dashboard data.";
    }
    if (error.status === 404) {
      return "Dashboard data was not found for this workspace.";
    }
    if (error.status === 409) {
      return "Dashboard data conflict. Refresh to load the latest state.";
    }
    if (error.status === 422) {
      return "Invalid dashboard request. Refresh and try again.";
    }
    if (error.status === 429) {
      return "Too many requests. Wait a moment and refresh.";
    }
    if (error.status >= 500 || error.code === "timeout") {
      return "Dashboard service is temporarily unavailable.";
    }
    return error.message;
  }
  if (error instanceof Error) return error.message;
  return "Unable to load dashboard.";
}

const EMPTY_OVERVIEW: DashboardOverview = {
  stats: [],
  suggestions: [],
  agenda: [],
  recentContent: [],
  recentActivity: [],
  platformHealth: [],
  storage: { usedBytes: 0, totalBytes: 1, label: "Media library" },
  healthSummary: "Dashboard unavailable",
  partial: true,
  warnings: [],
};

export function createDashboardApiService(repository: DashboardRepository) {
  return {
    async loadDashboard(): Promise<DashboardLoadResult> {
      try {
        if (!repository.loadOverview) {
          throw new Error("Dashboard repository does not support overview loading.");
        }

        const overview = await repository.loadOverview();
        return {
          ...overview,
          offline: false,
          error: overview.partial ? (overview.warnings[0] ?? null) : null,
        };
      } catch (error) {
        const message = mapDashboardError(error);
        const offline = isApiError(error) && error.code === "network_error";
        return {
          ...EMPTY_OVERVIEW,
          offline,
          error: message,
          warnings: [message],
          partial: true,
        };
      }
    },
  };
}

export type DashboardApiService = ReturnType<typeof createDashboardApiService>;

/** Client polling interval aligned with backend cache refresh cadence. */
export const DASHBOARD_POLL_INTERVAL_MS = 60_000;
