import { NOTIFICATION_PREFERENCES } from "@/constants/settings";
import type { NotificationPreferenceDto, UserProfileDto } from "@/lib/api/settings-types";
import type { WorkspaceDto } from "@/lib/api/workspace-types";
import type {
  AiProvider,
  NotificationChannelId,
  NotificationPreference,
  ProfileDefaults,
} from "@/lib/domain/settings";
import type { WorkspaceInfo } from "@/lib/domain/workspace";

const TYPE_CODE_TO_CHANNEL_ID: Record<string, NotificationChannelId> = {
  publishing: "publishing",
  generation: "ai",
  ai: "ai",
  scheduler: "publishing",
  analytics: "product",
  security: "billing",
  administration: "collaboration",
  system: "product",
};

const CHANNEL_ID_TO_TYPE_CODE: Record<NotificationChannelId, string> = {
  publishing: "publishing",
  ai: "generation",
  collaboration: "administration",
  billing: "security",
  product: "system",
};

export type ProfileState = ProfileDefaults & {
  readonly id: string;
  readonly version: number;
  readonly avatarUrl: string | null;
};

export function mapUserProfileDto(dto: UserProfileDto): ProfileState {
  return {
    id: dto.id,
    version: dto.version,
    fullName: dto.displayName,
    email: dto.email ?? "",
    jobTitle: "",
    bio: "",
    timezone: dto.timeZone,
    language: dto.locale,
    avatarUrl: dto.avatarUrl ?? null,
  };
}

export function mapWorkspaceDto(dto: WorkspaceDto): WorkspaceInfo {
  const shortName =
    dto.name
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? "")
      .join("") || dto.slug.slice(0, 2).toUpperCase();
  return {
    id: dto.id,
    version: dto.version,
    name: dto.name,
    shortName,
    description: `${dto.slug} · ${dto.timeZone}`,
    timeZone: dto.timeZone,
  };
}

export function mapNotificationPreferences(
  rows: readonly NotificationPreferenceDto[],
): NotificationPreference[] {
  const grouped = new Map<NotificationChannelId, { email: boolean; inApp: boolean }>();

  for (const row of rows) {
    const channelId = TYPE_CODE_TO_CHANNEL_ID[row.typeCode] ?? "product";
    const current = grouped.get(channelId) ?? { email: true, inApp: true };
    if (row.channel === "email") current.email = row.enabled;
    if (row.channel === "in_app") current.inApp = row.enabled;
    grouped.set(channelId, current);
  }

  return NOTIFICATION_PREFERENCES.map((catalog) => {
    const resolved = grouped.get(catalog.id);
    return {
      ...catalog,
      email: resolved?.email ?? catalog.email,
      inApp: resolved?.inApp ?? catalog.inApp,
    };
  });
}

export function toPreferenceUpdateRequests(
  preferences: Readonly<Record<NotificationChannelId, { email: boolean; inApp: boolean }>>,
): readonly import("@/lib/api/settings-types").NotificationPreferenceItemRequestDto[] {
  const items: import("@/lib/api/settings-types").NotificationPreferenceItemRequestDto[] = [];
  (
    Object.entries(preferences) as Array<
      [NotificationChannelId, { email: boolean; inApp: boolean }]
    >
  ).forEach(([channelId, state]) => {
    const typeCode = CHANNEL_ID_TO_TYPE_CODE[channelId];
    items.push({ typeCode, channel: "email", enabled: state.email, timeZone: "UTC" });
    items.push({ typeCode, channel: "in_app", enabled: state.inApp, timeZone: "UTC" });
  });
  return items;
}

export function mapProviderStatusToAiProvider(
  provider: import("@/lib/api/settings-types").ProviderStatusDto,
  index: number,
): AiProvider {
  const status =
    provider.status === "enabled"
      ? "connected"
      : provider.status === "degraded"
        ? "error"
        : "disconnected";
  return {
    id: provider.code,
    name: provider.name,
    model: provider.code,
    status,
    monthlyTokens: 0,
    isDefault: index === 0,
  };
}
