export type SettingsSectionId =
  | "profile"
  | "appearance"
  | "notifications"
  | "ai-providers"
  | "storage"
  | "publishing"
  | "security"
  | "api-keys"
  | "danger-zone";

export type NotificationChannelId = "publishing" | "ai" | "collaboration" | "billing" | "product";

export type NotificationPreference = {
  readonly id: NotificationChannelId;
  readonly label: string;
  readonly description: string;
  readonly email: boolean;
  readonly inApp: boolean;
};

export type AiProviderStatus = "connected" | "disconnected" | "error";

export type AiProvider = {
  readonly id: string;
  readonly name: string;
  readonly model: string;
  readonly status: AiProviderStatus;
  readonly monthlyTokens: number;
  readonly isDefault: boolean;
};

export type SessionRecord = {
  readonly id: string;
  readonly device: string;
  readonly location: string;
  readonly lastActive: string;
  readonly isCurrent: boolean;
};

export type ApiKeyScope = "read" | "write" | "admin";

export type ApiKeyRecord = {
  readonly id: string;
  readonly label: string;
  readonly maskedKey: string;
  readonly scope: ApiKeyScope;
  readonly createdAt: string;
  readonly lastUsedAt: string | null;
};

export type ProfileDefaults = {
  readonly fullName: string;
  readonly email: string;
  readonly jobTitle: string;
  readonly bio: string;
  readonly timezone: string;
  readonly language: string;
};

export type PublishingDefaults = {
  readonly defaultTimezone: string;
  readonly autoQueue: boolean;
  readonly requireApproval: boolean;
  readonly appendUtm: boolean;
  readonly retryFailed: boolean;
  readonly dailyLimit: string;
};

export type StorageUsage = {
  readonly usedBytes: number;
  readonly totalBytes: number;
  readonly breakdown: readonly {
    readonly id: string;
    readonly label: string;
    readonly bytes: number;
  }[];
  readonly region: string;
};
