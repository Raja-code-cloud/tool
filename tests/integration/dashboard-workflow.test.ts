import { describe, expect, it } from "vitest";

import { mockDashboardRepository } from "@/lib/adapters/mock-repositories";
import { mapDashboardStats } from "@/lib/dashboard/mappers";
import { createDashboardApiService } from "@/lib/services/dashboard-api-service";
import { createDashboardService } from "@/lib/services/workspace-services";

describe("dashboard workflow", () => {
  const service = createDashboardService(mockDashboardRepository);
  const apiService = createDashboardApiService(mockDashboardRepository);

  it("loads dashboard metrics, suggestions, and recent activity", async () => {
    expect((await service.listSuggestions()).length).toBeGreaterThan(0);
    expect((await service.listAgenda()).length).toBeGreaterThan(0);
    expect((await service.listRecentContent()).length).toBeGreaterThan(0);
    expect((await service.listRecentActivity()).length).toBeGreaterThan(0);
    expect((await service.listPlatformHealth()).length).toBeGreaterThan(0);
  });

  it("exposes storage usage and workspace health summary", async () => {
    const storage = await service.getStorage();
    expect(storage.usedBytes).toBeLessThanOrEqual(storage.totalBytes);
    expect(await service.getHealthSummary()).toMatch(/operational|attention/i);
  });

  it("loads overview via dashboard api service", async () => {
    const overview = await apiService.loadDashboard();
    expect(overview.stats.length).toBe(5);
    expect(overview.recentContent.length).toBeGreaterThan(0);
  });

  it("maps summary cards from backend count inputs", () => {
    const stats = mapDashboardStats({
      totalContent: { count: 47, partial: false },
      draftContent: { count: 12, partial: false },
      publishedContent: { count: 42, partial: false },
      scheduledContent: { count: 18, partial: false },
      failedContent: { count: 3, partial: false },
      todayScheduledCount: 6,
    });

    expect(stats.map((stat) => stat.id)).toEqual([
      "total-content",
      "scheduled-content",
      "published-content",
      "failed-content",
      "draft-content",
    ]);
  });
});
