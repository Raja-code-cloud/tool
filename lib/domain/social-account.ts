import type { PlatformId } from "@/lib/domain/platform";

export type FuturePlatformId = "threads" | "hashnode" | "devto" | "tiktok" | "newsletter";
export type SocialPlatformId = PlatformId | FuturePlatformId;
export type ConnectionStatus = "connected" | "disconnected";
export type HealthStatus = "healthy" | "warning" | "error" | "needs_reauth";
export type TokenStatus = "active" | "expiring_soon" | "expired" | "renew_required";
export type ActivityType =
  "connected" | "disconnected" | "publish_success" | "publish_failed" | "permission_changed";

export type SocialAccount = {
  readonly id: string;
  readonly platformId: SocialPlatformId;
  readonly platformName: string;
  readonly connectionStatus: ConnectionStatus;
  readonly healthStatus: HealthStatus;
  readonly tokenStatus: TokenStatus;
  readonly accountName: string;
  readonly displayName: string;
  readonly username: string;
  readonly accountType: string;
  readonly avatarFallback: string;
  readonly avatarHue: number;
  readonly lastSync: string;
  readonly connectedSince: string | null;
  readonly publishingEnabled: boolean;
  readonly followers: number;
  readonly permissions: readonly string[];
  readonly defaultAudience: string;
  readonly timezone: string;
  readonly defaultSettings: {
    readonly visibility: string;
    readonly hashtags: string;
    readonly autoPublish: boolean;
    readonly aiOptimization: boolean;
    readonly autoSchedule: boolean;
    readonly urlTracking: boolean;
  };
  readonly isComingSoon?: boolean;
};

export type ActivityEvent = {
  readonly id: string;
  readonly accountId: string;
  readonly platformName: string;
  readonly type: ActivityType;
  readonly message: string;
  readonly timestamp: string;
};

export type SocialAccountFilter =
  "all" | "connected" | "disconnected" | "healthy" | "error" | PlatformId;
