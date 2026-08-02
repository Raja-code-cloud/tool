import type { PlatformId } from "@/lib/domain/platform";
import type { SocialAccount, SocialAccountFilter } from "@/lib/domain/social-account";
import { formatCompactNumber } from "@/lib/utils/formatting";

export type SocialAccountsOverview = {
  connected: number;
  disconnected: number;
  publishingEnabled: number;
  publishingErrors: number;
  tokenExpiring: number;
};

export function computeOverview(accounts: readonly SocialAccount[]): SocialAccountsOverview {
  const active = accounts.filter((account) => !account.isComingSoon);
  return {
    connected: active.filter((account) => account.connectionStatus === "connected").length,
    disconnected: active.filter((account) => account.connectionStatus === "disconnected").length,
    publishingEnabled: active.filter((account) => account.publishingEnabled).length,
    publishingErrors: active.filter(
      (account) => account.healthStatus === "error" || account.healthStatus === "needs_reauth",
    ).length,
    tokenExpiring: active.filter(
      (account) =>
        account.tokenStatus === "expiring_soon" ||
        account.tokenStatus === "renew_required" ||
        account.tokenStatus === "expired",
    ).length,
  };
}

export function filterAccounts(
  accounts: readonly SocialAccount[],
  filter: SocialAccountFilter,
  search: string,
): SocialAccount[] {
  const query = search.trim().toLowerCase();
  return accounts.filter((account) => {
    if (account.isComingSoon)
      return filter === "all" && (!query || account.platformName.toLowerCase().includes(query));
    if (filter === "connected" && account.connectionStatus !== "connected") return false;
    if (filter === "disconnected" && account.connectionStatus !== "disconnected") return false;
    if (filter === "healthy" && account.healthStatus !== "healthy") return false;
    if (
      filter === "error" &&
      account.healthStatus !== "error" &&
      account.healthStatus !== "needs_reauth"
    )
      return false;
    if (
      ["linkedin", "facebook", "instagram", "x", "medium", "youtube"].includes(filter) &&
      account.platformId !== filter
    )
      return false;
    if (query) {
      const haystack = [
        account.platformName,
        account.accountName,
        account.displayName,
        account.username,
        account.accountType,
      ]
        .join(" ")
        .toLowerCase();
      if (!haystack.includes(query)) return false;
    }
    return true;
  });
}

export function formatFollowers(count: number): string {
  return formatCompactNumber(count, count >= 1_000 ? { minimumFractionDigits: 1 } : {});
}

export function isPlatformFilter(value: SocialAccountFilter): value is PlatformId {
  return ["linkedin", "facebook", "instagram", "x", "medium", "youtube"].includes(value);
}
