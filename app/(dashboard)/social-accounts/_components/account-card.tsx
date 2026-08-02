"use client";

import { motion } from "framer-motion";
import { ExternalLink, RefreshCw, Settings, Unplug } from "lucide-react";

import { OutlineButton, PrimaryButton, SecondaryButton } from "@/components/buttons";
import { PlatformChip } from "@/components/platform";
import { Avatar, Badge, Switch } from "@/components/ui";
import { getPlatformVisual, isPlatformId } from "@/lib/config/platforms";
import type { SocialAccount } from "@/lib/domain/social-account";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";
import { cn } from "@/lib/utils/cn";
import { formatDate } from "@/lib/utils/formatting";
import { formatFollowers } from "@/lib/utils/social-accounts";

import {
  ConnectionStatusBadge,
  HealthStatusBadge,
  TokenStatusBadge,
} from "./account-status-badges";

export type AccountActions = {
  onOpen: (id: string) => void;
  onReconnect: (id: string) => void;
  onDisconnect: (id: string) => void;
  onRefresh: (id: string) => void;
  onTogglePublishing: (id: string, enabled: boolean) => void;
};

export type AccountCardProps = {
  account: SocialAccount;
  actions: AccountActions;
};

export function AccountCard({ account, actions }: AccountCardProps): React.JSX.Element {
  const visual = isPlatformId(account.platformId)
    ? getPlatformVisual(account.platformId)
    : undefined;
  const isComingSoon = account.isComingSoon === true;
  const connected = account.connectionStatus === "connected";

  return (
    <motion.article
      layout
      {...(!isComingSoon ? { whileHover: { y: -2 } } : {})}
      transition={{ duration: MOTION_DURATION.hover, ease: MOTION_EASING.enter }}
      className={cn(
        "bg-card hover:shadow-raised flex h-full flex-col rounded-xl border p-4 transition-shadow",
        isComingSoon && "opacity-75",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span
            className={cn(
              "grid size-10 place-items-center rounded-lg text-sm font-bold",
              visual?.bgClass ?? "bg-muted",
            )}
            aria-hidden="true"
          >
            {account.platformName.slice(0, 2).toUpperCase()}
          </span>
          <div>
            {isPlatformId(account.platformId) && <PlatformChip platform={account.platformId} />}
            <p className="mt-1 text-sm font-semibold">{account.platformName}</p>
          </div>
        </div>
        {isComingSoon ? (
          <Badge variant="neutral">Coming soon</Badge>
        ) : (
          <ConnectionStatusBadge status={account.connectionStatus} />
        )}
      </div>

      {!isComingSoon && (
        <>
          <div className="mt-4 flex items-center gap-3">
            <Avatar alt={account.displayName} fallback={account.avatarFallback} size="md" />
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">{account.accountName}</p>
              <p className="text-muted-foreground truncate text-xs">@{account.username}</p>
            </div>
          </div>

          <dl className="mt-4 grid gap-2 text-xs">
            <div className="flex justify-between gap-2">
              <dt className="text-muted-foreground">Account type</dt>
              <dd className="font-medium">{account.accountType}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-muted-foreground">Followers</dt>
              <dd className="font-medium tabular-nums">{formatFollowers(account.followers)}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-muted-foreground">Last sync</dt>
              <dd className="font-medium">
                {account.lastSync
                  ? formatDate(account.lastSync, { dateStyle: "medium", timeStyle: "short" })
                  : "—"}
              </dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-muted-foreground">Connected since</dt>
              <dd className="font-medium">
                {account.connectedSince
                  ? formatDate(account.connectedSince, { dateStyle: "medium" })
                  : "—"}
              </dd>
            </div>
          </dl>

          <div className="mt-3 flex flex-wrap gap-1.5">
            <HealthStatusBadge status={account.healthStatus} />
            <TokenStatusBadge status={account.tokenStatus} />
          </div>

          <div className="bg-muted/30 mt-3 flex items-center justify-between rounded-lg border px-3 py-2">
            <span className="text-xs font-medium">Publishing enabled</span>
            <Switch
              checked={account.publishingEnabled}
              disabled={!connected}
              aria-label={`Publishing enabled for ${account.accountName}`}
              onCheckedChange={(checked) =>
                actions.onTogglePublishing(account.id, checked === true)
              }
            />
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {connected ? (
              <>
                <SecondaryButton
                  type="button"
                  size="compact"
                  onClick={() => actions.onOpen(account.id)}
                >
                  <Settings className="size-4" aria-hidden="true" /> Configure
                </SecondaryButton>
                <OutlineButton
                  type="button"
                  size="compact"
                  onClick={() => actions.onRefresh(account.id)}
                >
                  <RefreshCw className="size-4" aria-hidden="true" /> Refresh
                </OutlineButton>
                <OutlineButton
                  type="button"
                  size="compact"
                  onClick={() => actions.onOpen(account.id)}
                >
                  <ExternalLink className="size-4" aria-hidden="true" /> View profile
                </OutlineButton>
                <SecondaryButton
                  type="button"
                  size="compact"
                  onClick={() => actions.onDisconnect(account.id)}
                >
                  <Unplug className="size-4" aria-hidden="true" /> Disconnect
                </SecondaryButton>
              </>
            ) : (
              <PrimaryButton
                type="button"
                size="compact"
                onClick={() => actions.onReconnect(account.id)}
              >
                Connect
              </PrimaryButton>
            )}
          </div>
        </>
      )}

      {isComingSoon && (
        <p className="text-muted-foreground mt-4 text-sm">
          {account.platformName} integration is on the roadmap. Stay tuned.
        </p>
      )}

      {!isComingSoon && (
        <button
          type="button"
          className="text-primary mt-auto pt-3 text-left text-xs font-semibold hover:underline"
          onClick={() => actions.onOpen(account.id)}
        >
          View details
        </button>
      )}
    </motion.article>
  );
}
