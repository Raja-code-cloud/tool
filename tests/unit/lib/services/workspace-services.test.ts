import { describe, expect, it } from "vitest";

import { CONTENT_LIBRARY_ITEMS } from "@/constants/content-library";
import { SCHEDULED_POSTS } from "@/constants/scheduler";
import { SOCIAL_ACCOUNTS } from "@/constants/social-accounts";
import {
  mockAiStudioRepository,
  mockAnalyticsRepository,
  mockContentRepository,
  mockDashboardRepository,
  mockSchedulerRepository,
  mockSettingsRepository,
  mockSocialAccountRepository,
  mockWorkspaceRepository,
} from "@/lib/adapters/mock-repositories";
import type { AnalyticsRepository, ContentRepository } from "@/lib/domain/repositories";
import {
  createAiStudioService,
  createAnalyticsService,
  createContentService,
  createDashboardService,
  createSchedulerService,
  createSettingsService,
  createSocialAccountService,
  createWorkspaceService,
} from "@/lib/services/workspace-services";

describe("workspace services", () => {
  it("returns content library data from the content repository", () => {
    const repository: ContentRepository = { list: () => CONTENT_LIBRARY_ITEMS.slice(0, 2) };
    expect(createContentService(repository).list()).toHaveLength(2);
  });

  it("returns scheduler posts and notifications", () => {
    const service = createSchedulerService(mockSchedulerRepository);
    expect(service.listPosts().length).toBeGreaterThan(0);
    expect(service.listNotifications().length).toBeGreaterThan(0);
  });

  it("returns social account data", () => {
    const service = createSocialAccountService(mockSocialAccountRepository);
    expect(service.listAccounts().length).toBeGreaterThan(SOCIAL_ACCOUNTS.length - 1);
    expect(service.listActivity().length).toBeGreaterThan(0);
  });

  it("returns ai studio project and suggestions", async () => {
    const service = createAiStudioService(mockAiStudioRepository);
    const project = await service.getProject();
    const suggestions = await service.listSuggestions();
    const generated = await service.generate({
      platform: "linkedin",
      tone: "professional",
      length: "medium",
      audience: "architects",
      generateHashtags: true,
      generateCta: true,
    });

    expect(project.name).toBeTruthy();
    expect(suggestions.length).toBeGreaterThan(0);
    expect(generated.content).toBeTruthy();
  });

  it("returns dashboard overview datasets", () => {
    const service = createDashboardService(mockDashboardRepository);
    expect(service.listRecentContent().length).toBeGreaterThan(0);
    expect(service.getHealthSummary()).toContain("operational");
    expect(service.getStorage().usedBytes).toBeGreaterThan(0);
  });

  it("filters analytics by platform and date range", () => {
    const service = createAnalyticsService(mockAnalyticsRepository);
    const filtered = service.filterPosts({ dateRange: "30d", platform: "linkedin" });
    expect(filtered.every((post) => post.platform === "linkedin")).toBe(true);

    const summary = service.computeSummary({ dateRange: "7d", platform: "all" });
    expect(summary.totalPosts).toBeGreaterThan(0);
    expect(summary.totalReach).toBeGreaterThan(0);

    const topPosts = service.getTopPosts({ dateRange: "30d", platform: "all" }, 3);
    expect(topPosts.length).toBeLessThanOrEqual(3);
    expect(topPosts[0]?.engagementRate).toBeGreaterThanOrEqual(topPosts[1]?.engagementRate ?? 0);
  });

  it("returns settings and workspace metadata", () => {
    const settings = createSettingsService(mockSettingsRepository);
    expect(settings.getProfileDefaults().fullName).toBeTruthy();
    expect(settings.listAiProviders().length).toBeGreaterThan(0);

    const workspace = createWorkspaceService(mockWorkspaceRepository);
    expect(workspace.getWorkspace().name).toBeTruthy();
    expect(workspace.getCurrentUser().email).toContain("@");
  });

  it("scales analytics datasets using repository date range factors", () => {
    const repository: AnalyticsRepository = {
      ...mockAnalyticsRepository,
      getDateRangeOptions: () => [{ label: "Today", value: "today", factor: 0.25 }],
      listPosts: () => mockAnalyticsRepository.listPosts().slice(0, 4),
    };
    const service = createAnalyticsService(repository);
    const summary = service.computeSummary({ dateRange: "today", platform: "all" });
    expect(summary.totalPosts).toBeGreaterThan(0);
    expect(
      service.getPublishingTrend({ dateRange: "today", platform: "all" })[0]?.posts,
    ).toBeDefined();
  });

  it("filters insights when a platform is selected", () => {
    const service = createAnalyticsService(mockAnalyticsRepository);
    const allInsights = service.getInsights({ dateRange: "30d", platform: "all" });
    const facebookInsights = service.getInsights({ dateRange: "30d", platform: "facebook" });
    expect(facebookInsights.length).toBeLessThanOrEqual(allInsights.length);
  });
});

describe("mock repository wiring", () => {
  it("exposes stable mock datasets for every domain repository", () => {
    expect(mockContentRepository.list()).toBe(CONTENT_LIBRARY_ITEMS);
    expect(mockSchedulerRepository.listPosts()).toBe(SCHEDULED_POSTS);
    expect(mockDashboardRepository.listSuggestions().length).toBeGreaterThan(0);
    expect(mockSettingsRepository.listApiKeys().length).toBeGreaterThan(0);
  });
});
