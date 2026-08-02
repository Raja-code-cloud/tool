import type {
  PreferencesEnvelope,
  ProfileEnvelope,
  ProvidersEnvelope,
  UpdateNotificationPreferencesRequestDto,
  UpdateUserProfileRequestDto,
} from "@/lib/api/settings-types";
import type { ApiClient } from "@/lib/api/client";
import type { PagedSuccessEnvelope } from "@/lib/api/asset-types";
import type {
  AiProvider,
  ApiKeyRecord,
  NotificationPreference,
  PublishingDefaults,
  SessionRecord,
  StorageUsage,
} from "@/lib/domain/settings";
import type { SettingsRepository } from "@/lib/domain/repositories";
import {
  mapNotificationPreferences,
  mapProviderStatusToAiProvider,
  mapUserProfileDto,
  toPreferenceUpdateRequests,
  type ProfileState,
} from "@/lib/settings/mappers";
import type { NotificationChannelId } from "@/lib/domain/settings";

function etag(version: number): Record<string, string> {
  return { "If-Match": `"${version}"` };
}

export function createHttpSettingsRepository(client: ApiClient): SettingsRepository {
  let cachedProfile: ProfileState | null = null;

  return {
    async getProfile() {
      const response = await client.get<ProfileEnvelope>("/api/v1/users/me");
      cachedProfile = mapUserProfileDto(response.data.data);
      return cachedProfile;
    },

    async updateProfile(input: UpdateUserProfileRequestDto, version: number) {
      const body: UpdateUserProfileRequestDto = {};
      if (input.displayName !== undefined) body.displayName = input.displayName;
      if (input.locale !== undefined) body.locale = input.locale;
      if (input.timeZone !== undefined) body.timeZone = input.timeZone;
      if (input.avatarObjectKey !== undefined) body.avatarObjectKey = input.avatarObjectKey;

      const response = await client.patch<ProfileEnvelope>("/api/v1/users/me", body, {
        headers: etag(version),
      });
      cachedProfile = mapUserProfileDto(response.data.data);
      return cachedProfile;
    },

    async uploadAvatar(file: File, version: number) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("assetType", "thumbnail");
      formData.append("title", "Profile avatar");

      const upload = await client.postForm<{ data: { objectKey?: string; id?: string } }>(
        "/api/v1/assets/upload",
        formData,
      );
      const objectKey =
        (upload.data as { data?: { objectKey?: string } }).data?.objectKey ??
        (upload.data as { data?: { id?: string } }).data?.id;
      if (!objectKey) {
        throw new Error("Avatar upload did not return an object key.");
      }
      const response = await client.patch<ProfileEnvelope>(
        "/api/v1/users/me",
        { avatarObjectKey: objectKey },
        { headers: etag(version) },
      );
      cachedProfile = mapUserProfileDto(response.data.data);
      return cachedProfile;
    },

    async listNotificationPreferences() {
      const response = await client.get<PreferencesEnvelope>("/api/v1/notifications/preferences");
      return mapNotificationPreferences(response.data.data);
    },

    async updateNotificationPreferences(
      preferences: Readonly<Record<NotificationChannelId, { email: boolean; inApp: boolean }>>,
    ) {
      const body: UpdateNotificationPreferencesRequestDto = {
        preferences: toPreferenceUpdateRequests(preferences),
      };
      const response = await client.patch<PreferencesEnvelope>(
        "/api/v1/notifications/preferences",
        body,
      );
      return mapNotificationPreferences(response.data.data);
    },

    async listAiProviders() {
      try {
        const response = await client.get<ProvidersEnvelope>(
          "/api/v1/admin/providers?providerType=ai",
        );
        return response.data.data.map(mapProviderStatusToAiProvider);
      } catch {
        return [] as readonly AiProvider[];
      }
    },

    async getStorageUsage(): Promise<StorageUsage> {
      return {
        usedBytes: 0,
        totalBytes: 0,
        breakdown: [],
        region: "unknown",
      };
    },

    async getPublishingDefaults(): Promise<PublishingDefaults> {
      const profile = cachedProfile ?? (await createHttpSettingsRepository(client).getProfile());
      return {
        defaultTimezone: profile.timezone,
        autoQueue: true,
        requireApproval: false,
        appendUtm: true,
        retryFailed: true,
        dailyLimit: "25",
      };
    },

    async listActiveSessions(): Promise<readonly SessionRecord[]> {
      return [];
    },

    async listApiKeys(): Promise<readonly ApiKeyRecord[]> {
      return [];
    },

    async getUnreadNotificationCount() {
      const response = await client.get<PagedSuccessEnvelope<{ readonly id: string }>>(
        "/api/v1/notifications?read=false&limit=100",
      );
      return response.data.data.length;
    },
  };
}
