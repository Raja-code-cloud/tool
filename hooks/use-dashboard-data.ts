"use client";

import { useCallback, useEffect, useState } from "react";

import type { DashboardStatData } from "@/lib/domain/dashboard";
import type { DashboardLoadResult } from "@/lib/services/dashboard-api-service";
import {
  DASHBOARD_POLL_INTERVAL_MS,
  dashboardApiService,
  isBackendDashboardEnabled,
} from "@/lib/services";
import { mockDashboardRepository } from "@/lib/adapters/mock-repositories";
import { createDashboardApiService } from "@/lib/services/dashboard-api-service";

const mockDashboardApiService = createDashboardApiService(mockDashboardRepository);

const EMPTY_STATE: DashboardLoadResult = {
  stats: [],
  suggestions: [],
  agenda: [],
  recentContent: [],
  recentActivity: [],
  platformHealth: [],
  storage: { usedBytes: 0, totalBytes: 1, label: "Media library" },
  healthSummary: "Loading dashboard…",
  partial: false,
  warnings: [],
  offline: false,
  error: null,
};

export function useDashboardData(refreshKey = 0) {
  const [state, setState] = useState<DashboardLoadResult>(EMPTY_STATE);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const load = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const service = isBackendDashboardEnabled ? dashboardApiService : mockDashboardApiService;
      const result = await service.loadDashboard();
      setState(result);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [refreshKey]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!isBackendDashboardEnabled) return undefined;

    const intervalId = window.setInterval(() => {
      void load();
    }, DASHBOARD_POLL_INTERVAL_MS);

    return () => window.clearInterval(intervalId);
  }, [load]);

  return {
    ...state,
    isLoading,
    isRefreshing,
    reload: load,
  };
}

export type DashboardViewStats = readonly (DashboardStatData & {
  readonly iconId: string;
})[];
