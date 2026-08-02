import type {
  ActivityEventDto,
  AuthorizeSocialAccountResponseDto,
  ConnectSocialAccountRequestDto,
  PagedSuccessEnvelope,
  PublicationHistoryItemDto,
  SingleSuccessEnvelope,
  SocialAccountDto,
  SocialPlatformDto,
  SuccessEnvelope,
  UpdateSocialAccountRequestDto,
} from "@/lib/api/social-account-types";
import type { ApiClient } from "@/lib/api/client";
import type { ActivityEvent, SocialAccount } from "@/lib/domain/social-account";
import type { SocialAccountRepository } from "@/lib/domain/repositories";
import {
  mapActivityEventDto,
  mapDefaultSettingsUpdate,
  mapSocialAccountDto,
  mapSocialPlatformDto,
} from "@/lib/social-accounts/mappers";

async function fetchAllAccounts(client: ApiClient): Promise<readonly SocialAccountDto[]> {
  const items: SocialAccountDto[] = [];
  let cursor: string | undefined;
  let hasMore = true;

  while (hasMore) {
    const query = new URLSearchParams();
    if (cursor) query.set("cursor", cursor);
    query.set("limit", "100");
    const path = `/api/v1/social-accounts?${query.toString()}`;
    const response = await client.get<PagedSuccessEnvelope<SocialAccountDto>>(path);
    items.push(...response.data.data);
    const page = response.data.meta?.page;
    cursor = page?.nextCursor ?? undefined;
    hasMore = page?.hasMore ?? false;
    if (!page?.hasMore) break;
  }

  return items;
}

async function fetchAllActivity(client: ApiClient): Promise<readonly ActivityEventDto[]> {
  const items: ActivityEventDto[] = [];
  let cursor: string | undefined;
  let hasMore = true;

  while (hasMore) {
    const query = new URLSearchParams();
    if (cursor) query.set("cursor", cursor);
    query.set("limit", "100");
    const path = `/api/v1/social-accounts/activity?${query.toString()}`;
    const response = await client.get<PagedSuccessEnvelope<ActivityEventDto>>(path);
    items.push(...response.data.data);
    const page = response.data.meta?.page;
    cursor = page?.nextCursor ?? undefined;
    hasMore = page?.hasMore ?? false;
    if (!page?.hasMore) break;
  }

  return items;
}

export function createHttpSocialAccountRepository(client: ApiClient): SocialAccountRepository {
  return {
    async listAccounts() {
      const accounts = await fetchAllAccounts(client);
      return accounts.map(mapSocialAccountDto);
    },

    async listPlatforms() {
      const response = await client.get<SuccessEnvelope<readonly SocialPlatformDto[]>>(
        "/api/v1/social-accounts/platforms",
      );
      return response.data.data.map(mapSocialPlatformDto);
    },

    async listActivity() {
      const events = await fetchAllActivity(client);
      return events.map(mapActivityEventDto);
    },

    async beginAuthorization(platformCode, redirectUri) {
      const response = await client.post<SingleSuccessEnvelope<AuthorizeSocialAccountResponseDto>>(
        "/api/v1/social-accounts/authorize",
        { platformCode, redirectUri },
      );
      const data = response.data.data;
      return {
        authorizationUrl: data.authorizationUrl,
        state: data.state,
        codeVerifier: data.codeVerifier,
        platformCode: data.platformCode,
      };
    },

    async connectAccount(input) {
      const body: ConnectSocialAccountRequestDto = {
        platformCode: input.platformCode,
        authorizationCode: input.authorizationCode,
        codeVerifier: input.codeVerifier,
        redirectUri: input.redirectUri,
        state: input.state,
      };
      const response = await client.post<SingleSuccessEnvelope<SocialAccountDto>>(
        "/api/v1/social-accounts/connect",
        body,
      );
      return mapSocialAccountDto(response.data.data);
    },

    async disconnectAccount(accountId) {
      const response = await client.post<SingleSuccessEnvelope<SocialAccountDto>>(
        `/api/v1/social-accounts/${accountId}/disconnect`,
      );
      return mapSocialAccountDto(response.data.data);
    },

    async refreshAccount(accountId) {
      const response = await client.post<SingleSuccessEnvelope<SocialAccountDto>>(
        `/api/v1/social-accounts/${accountId}/refresh`,
      );
      return mapSocialAccountDto(response.data.data);
    },

    async updateAccount(accountId, version, input) {
      const body: UpdateSocialAccountRequestDto = {};
      if (input.publishingEnabled !== undefined) {
        body.publishingEnabled = input.publishingEnabled;
      }
      if (input.defaultSettings) {
        body.defaultSettings = mapDefaultSettingsUpdate(input.defaultSettings);
      }
      const response = await client.patch<SingleSuccessEnvelope<SocialAccountDto>>(
        `/api/v1/social-accounts/${accountId}`,
        body,
        { headers: { "If-Match": String(version) } },
      );
      return mapSocialAccountDto(response.data.data);
    },

    async listPublicationHistory(socialAccountId) {
      const query = new URLSearchParams();
      if (socialAccountId) query.set("socialAccountId", socialAccountId);
      query.set("limit", "50");
      const path = `/api/v1/publish/history?${query.toString()}`;
      const response = await client.get<PagedSuccessEnvelope<PublicationHistoryItemDto>>(path);
      return response.data.data;
    },
  };
}

export function createMockSocialAccountRepository(
  accounts: readonly import("@/lib/domain/social-account").SocialAccount[],
  activity: readonly import("@/lib/domain/social-account").ActivityEvent[],
): SocialAccountRepository {
  type StoredAccount = SocialAccount & { readonly version: number };
  let store: StoredAccount[] = accounts.map((account, index) => ({
    ...account,
    version: account.version ?? index + 1,
  }));

  return {
    async listAccounts() {
      return store;
    },

    async listPlatforms() {
      return [
        { id: "linkedin", code: "linkedin", name: "LinkedIn", isComingSoon: false },
        { id: "facebook", code: "facebook", name: "Facebook", isComingSoon: false },
        { id: "instagram", code: "instagram", name: "Instagram", isComingSoon: false },
        { id: "x", code: "x", name: "X (Twitter)", isComingSoon: false },
        { id: "medium", code: "medium", name: "Medium", isComingSoon: false },
        { id: "youtube", code: "youtube", name: "YouTube", isComingSoon: false },
      ];
    },

    async listActivity() {
      return activity;
    },

    async beginAuthorization(platformCode, redirectUri) {
      const state = `mock-state-${Date.now()}`;
      const codeVerifier = `mock-verifier-${Date.now()}`;
      const code = `mock-code-${Date.now()}`;
      const url = new URL(redirectUri);
      url.searchParams.set("code", code);
      url.searchParams.set("state", state);
      return {
        authorizationUrl: url.toString(),
        state,
        codeVerifier,
        platformCode,
      };
    },

    async connectAccount(input) {
      const created: StoredAccount = {
        id: `acc-${input.platformCode}-${Date.now()}`,
        version: 1,
        platformId: input.platformCode as import("@/lib/domain/platform").PlatformId,
        platformName: input.platformCode,
        connectionStatus: "connected",
        healthStatus: "healthy",
        tokenStatus: "active",
        accountName: "Connected account",
        displayName: "Connected account",
        username: input.platformCode,
        accountType: "Account",
        avatarFallback: "CA",
        avatarHue: 180,
        lastSync: new Date().toISOString(),
        connectedSince: new Date().toISOString(),
        publishingEnabled: true,
        followers: 0,
        permissions: ["Publish posts"],
        defaultAudience: "",
        timezone: "UTC",
        defaultSettings: {
          visibility: "Public",
          hashtags: "",
          autoPublish: false,
          aiOptimization: true,
          autoSchedule: false,
          urlTracking: true,
        },
      };
      store = [...store, created];
      return created;
    },

    async disconnectAccount(accountId) {
      const index = store.findIndex((account) => account.id === accountId);
      if (index < 0) throw new Error("Account not found");
      const updated: StoredAccount = {
        ...store[index]!,
        connectionStatus: "disconnected",
        healthStatus: "warning",
        tokenStatus: "expired",
        publishingEnabled: false,
        version: store[index]!.version + 1,
      };
      store = [...store.slice(0, index), updated, ...store.slice(index + 1)];
      return updated;
    },

    async refreshAccount(accountId) {
      const index = store.findIndex((account) => account.id === accountId);
      if (index < 0) throw new Error("Account not found");
      const updated: StoredAccount = {
        ...store[index]!,
        connectionStatus: "connected",
        healthStatus: "healthy",
        tokenStatus: "active",
        lastSync: new Date().toISOString(),
        version: store[index]!.version + 1,
      };
      store = [...store.slice(0, index), updated, ...store.slice(index + 1)];
      return updated;
    },

    async updateAccount(accountId, version, input) {
      const index = store.findIndex((account) => account.id === accountId);
      if (index < 0) throw new Error("Account not found");
      const current = store[index]!;
      const updated: StoredAccount = {
        ...current,
        publishingEnabled: input.publishingEnabled ?? current.publishingEnabled,
        defaultSettings: input.defaultSettings
          ? { ...current.defaultSettings, ...input.defaultSettings }
          : current.defaultSettings,
        version: version + 1,
      };
      store = [...store.slice(0, index), updated, ...store.slice(index + 1)];
      return updated;
    },

    async listPublicationHistory() {
      return [];
    },
  };
}
