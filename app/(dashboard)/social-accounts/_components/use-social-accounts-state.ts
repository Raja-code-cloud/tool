"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ROUTES } from "@/constants/navigation";
import { useToast } from "@/hooks/use-toast";
import { isApiError } from "@/lib/api/errors";
import type { SocialAccount, SocialAccountFilter } from "@/lib/domain/social-account";
import { socialAccountService } from "@/lib/services";
import { resolveSocialAccountErrorMessage } from "@/lib/social-accounts/error-messages";
import {
  SOCIAL_OAUTH_PLATFORM_KEY,
  SOCIAL_OAUTH_RETURN_TO_KEY,
  SOCIAL_OAUTH_STATE_KEY,
  SOCIAL_OAUTH_VERIFIER_KEY,
} from "@/lib/social-accounts/oauth-storage";
import { computeOverview, filterAccounts } from "@/lib/utils/social-accounts";
import { SUPPORTED_PLATFORMS } from "@/lib/config/social-accounts";
import { isPlatformId } from "@/lib/config/platforms";

function resolveMockAuthorizationUrl(authorizationUrl: string): string {
  if (!authorizationUrl.startsWith("mock://")) {
    return authorizationUrl;
  }
  const normalized = authorizationUrl.replace("mock://", "https://mock.local/");
  const parsed = new URL(normalized);
  const redirectUri = parsed.searchParams.get("redirect_uri");
  const code = parsed.searchParams.get("code");
  const state = parsed.searchParams.get("state");
  if (!redirectUri || !code || !state) {
    return authorizationUrl;
  }
  const target = new URL(redirectUri);
  target.searchParams.set("code", code);
  target.searchParams.set("state", state);
  return target.toString();
}

export function useSocialAccountsState() {
  const { toast } = useToast();
  const [accounts, setAccounts] = useState<readonly SocialAccount[]>([]);
  const [activityEvents, setActivityEvents] = useState<
    readonly import("@/lib/domain/social-account").ActivityEvent[]
  >([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<SocialAccountFilter>("all");
  const [search, setSearch] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [connectOpen, setConnectOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const loadAccounts = useCallback(async () => {
    setLoadError(null);
    try {
      const [nextAccounts, nextActivity] = await Promise.all([
        socialAccountService.listAccounts(),
        socialAccountService.listActivity(),
      ]);
      setAccounts(nextAccounts);
      setActivityEvents(nextActivity);
    } catch (error) {
      const message = resolveSocialAccountErrorMessage(error);
      setLoadError(message);
      toast({
        title: "Unable to load accounts",
        description: message,
      });
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    void loadAccounts();
  }, [loadAccounts]);

  const selectedAccount = useMemo(
    () => accounts.find((account) => account.id === selectedId) ?? null,
    [accounts, selectedId],
  );

  const filteredAccounts = useMemo(
    () => filterAccounts(accounts, filter, search),
    [accounts, filter, search],
  );

  const overview = useMemo(() => computeOverview(accounts), [accounts]);

  const activeAccounts = useMemo(
    () => filteredAccounts.filter((account) => !account.isComingSoon),
    [filteredAccounts],
  );

  const comingSoonAccounts = useMemo(
    () => filteredAccounts.filter((account) => account.isComingSoon),
    [filteredAccounts],
  );

  const showEmpty = !isLoading && activeAccounts.length === 0 && comingSoonAccounts.length === 0;

  const openAccount = useCallback((id: string) => {
    setSelectedId(id);
    setDrawerOpen(true);
  }, []);

  const refresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await loadAccounts();
      toast({ title: "Connections refreshed", description: "Account sync status updated." });
    } catch (error) {
      toast({
        title: "Refresh failed",
        description: resolveSocialAccountErrorMessage(error),
      });
    } finally {
      setIsRefreshing(false);
    }
  }, [loadAccounts, toast]);

  const connectAccount = useCallback(
    async (platformName: string) => {
      const platform = SUPPORTED_PLATFORMS.find((entry) => entry.label === platformName);
      if (!platform) {
        toast({
          title: "Unsupported platform",
          description: "This platform is not available for connection.",
        });
        return;
      }

      try {
        const redirectUri = `${window.location.origin}${ROUTES.socialCallback}`;
        const flow = await socialAccountService.beginAuthorization(platform.id, redirectUri);
        sessionStorage.setItem(SOCIAL_OAUTH_STATE_KEY, flow.state);
        sessionStorage.setItem(SOCIAL_OAUTH_VERIFIER_KEY, flow.codeVerifier);
        sessionStorage.setItem(SOCIAL_OAUTH_PLATFORM_KEY, flow.platformCode);
        sessionStorage.setItem(SOCIAL_OAUTH_RETURN_TO_KEY, ROUTES.socialAccounts);
        setConnectOpen(false);
        window.location.assign(resolveMockAuthorizationUrl(flow.authorizationUrl));
      } catch (error) {
        toast({
          title: "Connect failed",
          description: resolveSocialAccountErrorMessage(error),
        });
      }
    },
    [toast],
  );

  const disconnectAccount = useCallback(
    async (id: string) => {
      try {
        const updated = await socialAccountService.disconnectAccount(id);
        setAccounts((prev) => prev.map((account) => (account.id === id ? updated : account)));
        toast({
          title: "Account disconnected",
          description: "Publishing has been disabled for this account.",
        });
      } catch (error) {
        toast({
          title: "Disconnect failed",
          description: resolveSocialAccountErrorMessage(error),
        });
      }
    },
    [toast],
  );

  const reconnectAccount = useCallback(
    async (id: string) => {
      try {
        const updated = await socialAccountService.refreshAccount(id);
        setAccounts((prev) => prev.map((account) => (account.id === id ? updated : account)));
        toast({ title: "Reconnected", description: "Account connection restored." });
      } catch (error) {
        if (isApiError(error) && error.backendCode === "needs_reauth") {
          const account = accounts.find((entry) => entry.id === id);
          if (account && isPlatformId(account.platformId)) {
            await connectAccount(account.platformName);
            return;
          }
        }
        toast({
          title: "Reconnect failed",
          description: resolveSocialAccountErrorMessage(error),
        });
      }
    },
    [accounts, connectAccount, toast],
  );

  const togglePublishing = useCallback(
    async (id: string, enabled: boolean) => {
      const account = accounts.find((entry) => entry.id === id);
      if (!account?.version) {
        setAccounts((prev) =>
          prev.map((entry) => (entry.id === id ? { ...entry, publishingEnabled: enabled } : entry)),
        );
        return;
      }

      try {
        const updated = await socialAccountService.updateAccount(id, account.version, {
          publishingEnabled: enabled,
        });
        setAccounts((prev) => prev.map((entry) => (entry.id === id ? updated : entry)));
      } catch (error) {
        toast({
          title: "Update failed",
          description: resolveSocialAccountErrorMessage(error),
        });
      }
    },
    [accounts, toast],
  );

  const updateSettings = useCallback(
    async (id: string, settings: Partial<SocialAccount["defaultSettings"]>) => {
      const account = accounts.find((entry) => entry.id === id);
      if (!account?.version) {
        setAccounts((prev) =>
          prev.map((entry) =>
            entry.id === id
              ? { ...entry, defaultSettings: { ...entry.defaultSettings, ...settings } }
              : entry,
          ),
        );
        toast({ title: "Settings saved", description: "Default publishing settings updated." });
        return;
      }

      try {
        const updated = await socialAccountService.updateAccount(id, account.version, {
          defaultSettings: settings,
        });
        setAccounts((prev) => prev.map((entry) => (entry.id === id ? updated : entry)));
        toast({ title: "Settings saved", description: "Default publishing settings updated." });
      } catch (error) {
        toast({
          title: "Settings not saved",
          description: resolveSocialAccountErrorMessage(error),
        });
      }
    },
    [accounts, toast],
  );

  return {
    accounts,
    filteredAccounts,
    activeAccounts,
    comingSoonAccounts,
    selectedAccount,
    selectedId,
    filter,
    setFilter,
    search,
    setSearch,
    drawerOpen,
    setDrawerOpen,
    connectOpen,
    setConnectOpen,
    isRefreshing,
    isLoading,
    loadError,
    overview,
    showEmpty,
    openAccount,
    refresh,
    connectAccount,
    disconnectAccount,
    reconnectAccount,
    togglePublishing,
    updateSettings,
    activityEvents,
    reload: loadAccounts,
  };
}
