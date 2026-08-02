import { describe, expect, it } from "vitest";

import {
  computeOverview,
  filterAccounts,
  formatFollowers,
  isPlatformFilter,
} from "@/lib/utils/social-accounts";
import { socialAccountFactory } from "@/tests/factories";

describe("social accounts utilities", () => {
  it("computes account overview metrics", () => {
    const accounts = [
      socialAccountFactory.build({ connectionStatus: "connected", publishingEnabled: true }),
      socialAccountFactory.build({
        connectionStatus: "disconnected",
        healthStatus: "error",
        publishingEnabled: false,
      }),
    ];

    const overview = computeOverview(accounts);
    expect(overview.connected).toBe(1);
    expect(overview.disconnected).toBe(1);
    expect(overview.publishingEnabled).toBe(1);
    expect(overview.publishingErrors).toBe(1);
  });

  it("filters accounts by status, platform, and search query", () => {
    const accounts = [
      socialAccountFactory.build({
        platformId: "linkedin",
        platformName: "LinkedIn",
        accountName: "Cloud Hub",
      }),
      socialAccountFactory.build({ platformId: "x", platformName: "X", accountName: "Ops Team" }),
    ];

    expect(filterAccounts(accounts, "connected", "")).toHaveLength(2);
    expect(filterAccounts(accounts, "linkedin", "cloud")).toHaveLength(1);
    expect(isPlatformFilter("linkedin")).toBe(true);
    expect(isPlatformFilter("connected")).toBe(false);
  });

  it("formats follower counts compactly", () => {
    expect(formatFollowers(950)).toMatch(/950/);
    expect(formatFollowers(12500)).toMatch(/12\.?5K|12K/);
  });
});
