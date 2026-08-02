import { describe, expect, it } from "vitest";

import type { SocialAccountDto } from "@/lib/api/social-account-types";
import {
  mapActivityEventDto,
  mapDefaultSettingsUpdate,
  mapSocialAccountDto,
} from "@/lib/social-accounts/mappers";

const sampleAccount: SocialAccountDto = {
  id: "acc-1",
  version: 2,
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-02T00:00:00.000Z",
  platformId: "linkedin",
  platformName: "LinkedIn",
  connectionStatus: "connected",
  healthStatus: "healthy",
  tokenStatus: "active",
  accountName: "Jane Doe",
  displayName: "Jane Doe",
  username: "jane-doe",
  accountType: "Personal profile",
  avatarFallback: "JD",
  avatarHue: 120,
  lastSync: "2026-01-02T12:00:00.000Z",
  connectedSince: "2026-01-01T00:00:00.000Z",
  publishingEnabled: true,
  followers: 1000,
  permissions: ["Publish posts"],
  defaultAudience: "Engineers",
  timezone: "UTC",
  defaultSettings: {
    visibility: "Public",
    hashtags: "#cloud",
    autoPublish: true,
    aiOptimization: true,
    autoSchedule: false,
    urlTracking: true,
  },
};

describe("social account mappers", () => {
  it("maps account dto to domain model", () => {
    const account = mapSocialAccountDto(sampleAccount);
    expect(account.platformId).toBe("linkedin");
    expect(account.version).toBe(2);
    expect(account.defaultSettings.hashtags).toBe("#cloud");
  });

  it("maps null token status to active", () => {
    const account = mapSocialAccountDto({ ...sampleAccount, tokenStatus: null });
    expect(account.tokenStatus).toBe("active");
  });

  it("maps activity dto", () => {
    const event = mapActivityEventDto({
      id: "evt-1",
      accountId: "acc-1",
      platformName: "LinkedIn",
      type: "connected",
      message: "Account connected",
      timestamp: "2026-01-01T00:00:00.000Z",
    });
    expect(event.type).toBe("connected");
  });

  it("maps default settings update payload", () => {
    expect(
      mapDefaultSettingsUpdate({
        autoPublish: true,
        hashtags: "#ai",
      }).hashtags,
    ).toBe("#ai");
  });
});
