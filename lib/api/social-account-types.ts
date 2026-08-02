import type { PagedSuccessEnvelope, SingleSuccessEnvelope } from "@/lib/api/asset-types";
import type { SuccessEnvelope } from "@/lib/api/auth-types";

export type { PagedSuccessEnvelope, SingleSuccessEnvelope, SuccessEnvelope };

export type ConnectionStatusDto = "connected" | "disconnected";
export type HealthStatusDto = "healthy" | "warning" | "error" | "needs_reauth";
export type OAuthTokenStatusDto =
  "active" | "expiring_soon" | "expired" | "renew_required" | "revoked";
export type PlatformStatusDto = "enabled" | "disabled" | "coming_soon";
export type ActivityTypeDto =
  "connected" | "disconnected" | "publish_success" | "publish_failed" | "permission_changed";

export type DefaultSettingsDto = {
  readonly visibility: string | null;
  readonly hashtags: string | null;
  readonly autoPublish: boolean;
  readonly aiOptimization: boolean;
  readonly autoSchedule: boolean;
  readonly urlTracking: boolean;
};

export type SocialAccountDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly platformId: string;
  readonly platformName: string;
  readonly connectionStatus: ConnectionStatusDto;
  readonly healthStatus: HealthStatusDto;
  readonly tokenStatus: OAuthTokenStatusDto | null;
  readonly accountName: string;
  readonly displayName: string;
  readonly username: string | null;
  readonly accountType: string | null;
  readonly avatarFallback: string;
  readonly avatarHue: number;
  readonly lastSync: string | null;
  readonly connectedSince: string | null;
  readonly publishingEnabled: boolean;
  readonly followers: number;
  readonly permissions: readonly string[];
  readonly defaultAudience: string | null;
  readonly timezone: string;
  readonly defaultSettings: DefaultSettingsDto;
};

export type SocialPlatformDto = {
  readonly id: string;
  readonly code: string;
  readonly name: string;
  readonly status: PlatformStatusDto;
  readonly apiVersion: string | null;
};

export type AuthorizeSocialAccountRequestDto = {
  readonly platformCode: string;
  readonly redirectUri: string;
};

export type AuthorizeSocialAccountResponseDto = {
  readonly authorizationUrl: string;
  readonly state: string;
  readonly codeVerifier: string;
  readonly platformCode: string;
};

export type ConnectSocialAccountRequestDto = {
  readonly platformCode: string;
  readonly authorizationCode: string;
  readonly codeVerifier: string;
  readonly redirectUri: string;
  readonly state: string;
};

export type DefaultSettingsUpdateDto = {
  readonly visibility?: string | null;
  readonly hashtags?: string | null;
  readonly autoPublish?: boolean;
  readonly aiOptimization?: boolean;
  readonly autoSchedule?: boolean;
  readonly urlTracking?: boolean;
};

export type UpdateSocialAccountRequestDto = {
  readonly publishingEnabled?: boolean;
  readonly defaultSettings?: DefaultSettingsUpdateDto;
};

export type ActivityEventDto = {
  readonly id: string;
  readonly accountId: string;
  readonly platformName: string;
  readonly type: ActivityTypeDto;
  readonly message: string;
  readonly timestamp: string;
};

export type PublicationHistoryItemDto = {
  readonly id: string;
  readonly publicationId: string;
  readonly targetId: string;
  readonly stateType: string;
  readonly fromState: string | null;
  readonly toState: string;
  readonly reasonCode: string | null;
  readonly occurredAt: string;
};
