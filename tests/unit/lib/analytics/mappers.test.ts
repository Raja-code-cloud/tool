import { describe, expect, it } from "vitest";

import {
  buildPublishingTrend,
  mapDashboardSummary,
  mapPlatformEngagement,
  mapPostAnalyticsDto,
} from "@/lib/analytics/mappers";
import type {
  AnalyticsDashboardDto,
  PlatformAnalyticsDto,
  PostAnalyticsDto,
} from "@/lib/api/analytics-types";

describe("analytics mappers", () => {
  it("maps dashboard metrics into summary cards", () => {
    const dashboard: AnalyticsDashboardDto = {
      periodStart: "2026-07-01T00:00:00Z",
      periodEnd: "2026-08-01T00:00:00Z",
      timeZone: "UTC",
      freshThrough: "2026-08-01T23:00:00Z",
      methodologyVersion: 1,
      metrics: [
        { code: "totalPosts", value: "12", unit: "count", isEstimated: false },
        { code: "reach", value: "1500", unit: "count", isEstimated: false },
        { code: "engagements", value: "240", unit: "count", isEstimated: false },
        { code: "scheduledPosts", value: "3", unit: "count", isEstimated: false },
      ],
    };

    expect(mapDashboardSummary(dashboard, 12)).toEqual({
      totalPosts: 12,
      totalReach: 1500,
      totalEngagement: 240,
      followersGrowth: 0,
      scheduledPosts: 3,
      aiContentGenerated: 0,
    });
  });

  it("maps post analytics DTOs and builds publishing trend buckets", () => {
    const post: PostAnalyticsDto = {
      contentId: "0194e8b0-0000-7000-8000-000000000001",
      snapshotAt: "2026-08-02T14:00:00Z",
      reach: 1000,
      engagements: 50,
      clicks: 20,
      engagementRate: "0.05",
      metrics: [],
    };

    const mapped = mapPostAnalyticsDto(post, "linkedin");
    expect(mapped.reach).toBe(1000);
    expect(mapped.engagementRate).toBe(5);

    const trend = buildPublishingTrend([mapped]);
    expect(trend.length).toBe(1);
    expect(trend[0]?.posts).toBe(1);
  });

  it("maps platform engagement aggregates", () => {
    const platforms: PlatformAnalyticsDto[] = [
      {
        platformId: "0194e8b0-0000-7000-8000-000000000010",
        platformCode: "linkedin",
        accountCount: 2,
        freshThrough: "2026-08-02T00:00:00Z",
        metrics: [{ code: "engagements", value: "500", unit: "count", isEstimated: false }],
      },
    ];

    expect(mapPlatformEngagement(platforms)).toEqual([
      { platform: "linkedin", label: "LinkedIn", engagement: 500 },
    ]);
  });
});
