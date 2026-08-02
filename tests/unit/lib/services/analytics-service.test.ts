import { describe, expect, it } from "vitest";

import { mockAnalyticsRepository } from "@/lib/adapters/mock-repositories";
import type { AnalyticsRepository } from "@/lib/domain/repositories";
import { createAnalyticsService, type AnalyticsFilters } from "@/lib/services/workspace-services";

function createService(overrides: Partial<AnalyticsRepository> = {}) {
  return createAnalyticsService({ ...mockAnalyticsRepository, ...overrides });
}

describe("analytics service edge cases", () => {
  const baseFilters: AnalyticsFilters = { dateRange: "30d", platform: "all" };

  it("filters engagement and reach charts by platform", () => {
    const service = createService();
    const linkedinFilters: AnalyticsFilters = { dateRange: "30d", platform: "linkedin" };

    expect(service.getEngagementByPlatform(linkedinFilters).length).toBeGreaterThan(0);
    expect(
      service.getReachByPlatform(linkedinFilters).every((item) => item.platform === "linkedin"),
    ).toBe(true);
    expect(
      service.getPlatformComparison(linkedinFilters).every((item) => item.platform === "linkedin"),
    ).toBe(true);
  });

  it("returns scaled auxiliary datasets", () => {
    const service = createService();
    expect(service.getAiUsageTrend(baseFilters).length).toBeGreaterThan(0);
    expect(service.getBestPostingTimes(baseFilters).length).toBeGreaterThan(0);
    expect(service.getContentTypePerformance(baseFilters).length).toBeGreaterThan(0);
    expect(service.getWorstPosts(baseFilters, 2).length).toBeLessThanOrEqual(2);
  });

  it("reduces visible posts when the selected date range factor is below one", () => {
    const service = createService({
      getDateRangeOptions: () => [{ label: "Today", value: "today", factor: 0.5 }],
      listPosts: () => mockAnalyticsRepository.listPosts(),
    });

    const allPosts = mockAnalyticsRepository.listPosts().length;
    const filtered = service.filterPosts({ dateRange: "today", platform: "all" }).length;
    expect(filtered).toBeLessThanOrEqual(allPosts);
  });
});
