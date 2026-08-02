import type { SocialAccount } from "@/lib/domain/social-account";

import { createFactory } from "./create-factory";

export const socialAccountFactory = createFactory<SocialAccount>((sequence) => ({
  id: `account-${sequence}`,
  platformId: "linkedin",
  platformName: "LinkedIn",
  connectionStatus: "connected",
  healthStatus: "healthy",
  tokenStatus: "active",
  accountName: `Account ${sequence}`,
  displayName: `Display ${sequence}`,
  username: `user${sequence}`,
  accountType: "Company Page",
  avatarFallback: "LI",
  avatarHue: 210,
  lastSync: "2026-08-01T10:00:00.000Z",
  connectedSince: "2026-01-01T00:00:00.000Z",
  publishingEnabled: true,
  followers: 12_500,
  permissions: ["publish", "read"],
  defaultAudience: "Public",
  timezone: "America/New_York",
  defaultSettings: {
    visibility: "public",
    hashtags: "#cloud",
    autoPublish: false,
    aiOptimization: true,
    autoSchedule: false,
    urlTracking: true,
  },
}));
