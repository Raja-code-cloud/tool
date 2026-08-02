import type { SingleSuccessEnvelope, SuccessEnvelope } from "@/lib/api/auth-types";

export type UserProfileDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly email: string | null;
  readonly displayName: string;
  readonly avatarUrl?: string | null;
  readonly locale: string;
  readonly timeZone: string;
  readonly status: "active" | "disabled" | "anonymized";
};

export type UpdateUserProfileRequestDto = {
  readonly displayName?: string;
  readonly locale?: string;
  readonly timeZone?: string;
  readonly avatarObjectKey?: string | null;
};

export type NotificationPreferenceDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly typeCode: string;
  readonly channel: "in_app" | "email" | "webhook";
  readonly enabled: boolean;
  readonly quietHoursStart?: string | null;
  readonly quietHoursEnd?: string | null;
  readonly timeZone: string;
};

export type NotificationPreferenceItemRequestDto = {
  readonly typeCode: string;
  readonly channel: "in_app" | "email" | "webhook";
  readonly enabled: boolean;
  readonly quietHoursStart?: string | null;
  readonly quietHoursEnd?: string | null;
  readonly timeZone?: string;
};

export type UpdateNotificationPreferencesRequestDto = {
  readonly preferences: readonly NotificationPreferenceItemRequestDto[];
};

export type ProviderStatusDto = {
  readonly providerType: string;
  readonly code: string;
  readonly name: string;
  readonly status: "enabled" | "disabled" | "degraded";
  readonly checkedAt: string;
  readonly message?: string | null;
};

export type ProfileEnvelope = SingleSuccessEnvelope<UserProfileDto>;
export type PreferencesEnvelope = SuccessEnvelope<readonly NotificationPreferenceDto[]>;
export type ProvidersEnvelope = SuccessEnvelope<readonly ProviderStatusDto[]>;
