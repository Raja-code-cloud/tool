import { describe, expect, it } from "vitest";

import { mockDashboardRepository } from "@/lib/adapters/mock-repositories";
import { createDashboardService } from "@/lib/services/workspace-services";

describe("dashboard workflow", () => {
  const service = createDashboardService(mockDashboardRepository);

  it("loads dashboard metrics, suggestions, and recent activity", () => {
    expect(service.listSuggestions().length).toBeGreaterThan(0);
    expect(service.listAgenda().length).toBeGreaterThan(0);
    expect(service.listRecentContent().length).toBeGreaterThan(0);
    expect(service.listRecentActivity().length).toBeGreaterThan(0);
    expect(service.listPlatformHealth().length).toBeGreaterThan(0);
  });

  it("exposes storage usage and workspace health summary", () => {
    expect(service.getStorage().usedBytes).toBeLessThanOrEqual(service.getStorage().totalBytes);
    expect(service.getHealthSummary()).toMatch(/operational|attention/i);
  });
});
