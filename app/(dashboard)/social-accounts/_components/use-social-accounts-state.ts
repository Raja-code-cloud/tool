"use client";

import { useCallback, useMemo, useState } from "react";

import { useToast } from "@/hooks/use-toast";
import type { SocialAccount, SocialAccountFilter } from "@/lib/domain/social-account";
import { socialAccountService } from "@/lib/services";
import { computeOverview, filterAccounts } from "@/lib/utils/social-accounts";

export function useSocialAccountsState() {
  const { toast } = useToast();
  const [accounts, setAccounts] = useState<readonly SocialAccount[]>(() =>
    socialAccountService.listAccounts(),
  );
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<SocialAccountFilter>("all");
  const [search, setSearch] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [connectOpen, setConnectOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

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

  const showEmpty = activeAccounts.length === 0 && comingSoonAccounts.length === 0;

  const openAccount = useCallback((id: string) => {
    setSelectedId(id);
    setDrawerOpen(true);
  }, []);

  const refresh = useCallback(() => {
    setIsRefreshing(true);
    window.setTimeout(() => {
      setIsRefreshing(false);
      toast({ title: "Connections refreshed", description: "Account sync status updated." });
    }, 600);
  }, [toast]);

  const connectAccount = useCallback(
    (platformName: string) => {
      toast({
        title: "Connect initiated (mock)",
        description: `${platformName} OAuth flow would open here.`,
      });
      setConnectOpen(false);
    },
    [toast],
  );

  const disconnectAccount = useCallback(
    (id: string) => {
      setAccounts((prev) =>
        prev.map((account) =>
          account.id === id
            ? {
                ...account,
                connectionStatus: "disconnected",
                publishingEnabled: false,
                healthStatus: "warning",
                tokenStatus: "expired",
              }
            : account,
        ),
      );
      toast({
        title: "Account disconnected",
        description: "Publishing has been disabled for this account.",
      });
    },
    [toast],
  );

  const reconnectAccount = useCallback(
    (id: string) => {
      setAccounts((prev) =>
        prev.map((account) =>
          account.id === id
            ? {
                ...account,
                connectionStatus: "connected",
                healthStatus: "healthy",
                tokenStatus: "active",
                lastSync: new Date().toISOString(),
              }
            : account,
        ),
      );
      toast({ title: "Reconnected (mock)", description: "Account connection restored." });
    },
    [toast],
  );

  const togglePublishing = useCallback((id: string, enabled: boolean) => {
    setAccounts((prev) =>
      prev.map((account) =>
        account.id === id ? { ...account, publishingEnabled: enabled } : account,
      ),
    );
  }, []);

  const updateSettings = useCallback(
    (id: string, settings: Partial<SocialAccount["defaultSettings"]>) => {
      setAccounts((prev) =>
        prev.map((account) =>
          account.id === id
            ? { ...account, defaultSettings: { ...account.defaultSettings, ...settings } }
            : account,
        ),
      );
      toast({ title: "Settings saved", description: "Default publishing settings updated." });
    },
    [toast],
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
    overview,
    showEmpty,
    openAccount,
    refresh,
    connectAccount,
    disconnectAccount,
    reconnectAccount,
    togglePublishing,
    updateSettings,
    activityEvents: socialAccountService.listActivity(),
  };
}
