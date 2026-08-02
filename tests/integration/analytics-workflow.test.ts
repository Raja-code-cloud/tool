import { describe, expect, it } from "vitest";

import { mockAnalyticsRepository } from "@/lib/adapters/mock-repositories";
import { createAnalyticsService } from "@/lib/services/workspace-services";

describe("analytics workflow", () => {
  const service = createAnalyticsService(mockAnalyticsRepository);

  it("filters posts and computes summary metrics for selected ranges", () => {
    const filters = { dateRange: "30d" as const, platform: "linkedin" as const };
    const posts = service.filterPosts(filters);
    const summary = service.computeSummary(filters);

    expect(posts.every((post) => post.platform === "linkedin")).toBe(true);
    expect(summary.totalReach).toBeGreaterThan(0);
    expect(service.getTopPosts(filters, 5).length).toBeLessThanOrEqual(5);
  });

  it("returns chart datasets scaled to the active filters", () => {
    const filters = { dateRange: "7d" as const, platform: "all" as const };
    expect(service.getPublishingTrend(filters).length).toBeGreaterThan(0);
    expect(service.getEngagementByPlatform(filters).length).toBeGreaterThan(0);
    expect(service.getInsights(filters).length).toBeGreaterThan(0);
  });
});
