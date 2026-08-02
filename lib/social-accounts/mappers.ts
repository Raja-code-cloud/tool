import type {
  ActivityEventDto,
  DefaultSettingsDto,
  OAuthTokenStatusDto,
  SocialAccountDto,
  SocialPlatformDto,
} from "@/lib/api/social-account-types";
import { getPlatformVisual, isPlatformId } from "@/lib/config/platforms";
import type { PlatformId } from "@/lib/domain/platform";
import type {
  ActivityEvent,
  ActivityType,
  ConnectionStatus,
  HealthStatus,
  SocialAccount,
  TokenStatus,
} from "@/lib/domain/social-account";

function mapTokenStatus(status: OAuthTokenStatusDto | null): TokenStatus {
  if (status === null) return "active";
  return status;
}

function mapDefaultSettings(settings: DefaultSettingsDto): SocialAccount["defaultSettings"] {
  return {
    visibility: settings.visibility ?? "Public",
    hashtags: settings.hashtags ?? "",
    autoPublish: settings.autoPublish,
    aiOptimization: settings.aiOptimization,
    autoSchedule: settings.autoSchedule,
    urlTracking: settings.urlTracking,
  };
}

export function mapSocialAccountDto(dto: SocialAccountDto): SocialAccount {
  const platformId = isPlatformId(dto.platformId) ? dto.platformId : "linkedin";
  let platformName = dto.platformName;
  try {
    platformName = getPlatformVisual(platformId).label;
  } catch {
    // Keep backend-provided name when platform config is missing.
  }

  return {
    id: dto.id,
    version: dto.version,
    platformId,
    platformName,
    connectionStatus: dto.connectionStatus as ConnectionStatus,
    healthStatus: dto.healthStatus as HealthStatus,
    tokenStatus: mapTokenStatus(dto.tokenStatus),
    accountName: dto.accountName,
    displayName: dto.displayName,
    username: dto.username ?? "",
    accountType: dto.accountType ?? "Account",
    avatarFallback: dto.avatarFallback,
    avatarHue: dto.avatarHue,
    lastSync: dto.lastSync ?? new Date(0).toISOString(),
    connectedSince: dto.connectedSince,
    publishingEnabled: dto.publishingEnabled,
    followers: dto.followers,
    permissions: dto.permissions,
    defaultAudience: dto.defaultAudience ?? "",
    timezone: dto.timezone,
    defaultSettings: mapDefaultSettings(dto.defaultSettings),
    isComingSoon: false,
  };
}

export function mapActivityEventDto(dto: ActivityEventDto): ActivityEvent {
  return {
    id: dto.id,
    accountId: dto.accountId,
    platformName: dto.platformName,
    type: dto.type as ActivityType,
    message: dto.message,
    timestamp: dto.timestamp,
  };
}

export function mapSocialPlatformDto(dto: SocialPlatformDto): {
  readonly id: PlatformId | null;
  readonly code: string;
  readonly name: string;
  readonly isComingSoon: boolean;
} {
  return {
    id: isPlatformId(dto.code) ? dto.code : null,
    code: dto.code,
    name: dto.name,
    isComingSoon: dto.status === "coming_soon",
  };
}

export function mapDefaultSettingsUpdate(
  settings: Partial<SocialAccount["defaultSettings"]>,
): import("@/lib/api/social-account-types").DefaultSettingsUpdateDto {
  return {
    visibility: settings.visibility,
    hashtags: settings.hashtags,
    autoPublish: settings.autoPublish,
    aiOptimization: settings.aiOptimization,
    autoSchedule: settings.autoSchedule,
    urlTracking: settings.urlTracking,
  };
}
