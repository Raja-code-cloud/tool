"use client";

import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Link2, Unplug, XCircle } from "lucide-react";

import { DestructiveButton, PrimaryButton, SecondaryButton } from "@/components/buttons";
import { KeyValueList } from "@/components/common";
import { Dialog, DrawerContent } from "@/components/dialogs";
import { isPlatformId, PlatformChip } from "@/components/platform";
import { Avatar, Input, Label, Switch } from "@/components/ui";
import type { ActivityEvent, SocialAccount } from "@/lib/domain/social-account";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";
import { formatDate } from "@/lib/utils/formatting";
import { formatFollowers } from "@/lib/utils/social-accounts";

import {
  ConnectionStatusBadge,
  HealthStatusBadge,
  TokenStatusBadge,
} from "./account-status-badges";

export type AccountDetailsDrawerProps = {
  account: SocialAccount | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDisconnect: (id: string) => void;
  onReconnect: (id: string) => void;
  onTogglePublishing: (id: string, enabled: boolean) => void;
  onUpdateSettings: (id: string, settings: Partial<SocialAccount["defaultSettings"]>) => void;
};

export function AccountDetailsDrawer({
  account,
  open,
  onOpenChange,
  onDisconnect,
  onReconnect,
  onTogglePublishing,
  onUpdateSettings,
}: AccountDetailsDrawerProps): React.JSX.Element {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {account && !account.isComingSoon ? (
          <DrawerContent
            key={account.id}
            side="right"
            title={account.displayName}
            description={`${account.platformName} · ${account.accountType}`}
            className="max-w-lg"
          >
            <motion.div
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 16 }}
              transition={{ duration: MOTION_DURATION.drawer, ease: MOTION_EASING.enter }}
              className="grid gap-5"
            >
              <div className="flex items-center gap-4">
                <Avatar alt={account.displayName} fallback={account.avatarFallback} size="lg" />
                <div>
                  {isPlatformId(account.platformId) ? (
                    <PlatformChip platform={account.platformId} />
                  ) : (
                    <span className="text-xs font-semibold">{account.platformName}</span>
                  )}
                  <p className="text-muted-foreground mt-1 text-sm">@{account.username}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <ConnectionStatusBadge status={account.connectionStatus} />
                    <HealthStatusBadge status={account.healthStatus} />
                    <TokenStatusBadge status={account.tokenStatus} />
                  </div>
                </div>
              </div>

              <KeyValueList
                items={[
                  {
                    id: "connected",
                    term: "Connected date",
                    description: account.connectedSince
                      ? formatDate(account.connectedSince, { dateStyle: "long" })
                      : "Not connected",
                  },
                  {
                    id: "sync",
                    term: "Last sync",
                    description: account.lastSync
                      ? formatDate(account.lastSync, { dateStyle: "long", timeStyle: "short" })
                      : "—",
                  },
                  {
                    id: "followers",
                    term: "Followers",
                    description: formatFollowers(account.followers),
                  },
                  {
                    id: "audience",
                    term: "Default audience",
                    description: account.defaultAudience,
                  },
                  { id: "timezone", term: "Timezone", description: account.timezone },
                ]}
              />

              <section aria-labelledby="permissions-heading">
                <h3 id="permissions-heading" className="text-sm font-semibold">
                  Granted permissions
                </h3>
                <ul className="text-muted-foreground mt-2 grid gap-1 text-sm">
                  {account.permissions.length > 0 ? (
                    account.permissions.map((permission) => (
                      <li key={permission}>• {permission}</li>
                    ))
                  ) : (
                    <li>No permissions granted</li>
                  )}
                </ul>
              </section>

              <section aria-labelledby="publishing-heading">
                <h3 id="publishing-heading" className="text-sm font-semibold">
                  Publishing status
                </h3>
                <div className="mt-2 flex items-center justify-between rounded-lg border px-3 py-2">
                  <Label htmlFor="drawer-publishing">Enable publishing</Label>
                  <Switch
                    id="drawer-publishing"
                    checked={account.publishingEnabled}
                    disabled={account.connectionStatus !== "connected"}
                    onCheckedChange={(checked) => onTogglePublishing(account.id, checked === true)}
                  />
                </div>
              </section>

              <section aria-labelledby="defaults-heading">
                <h3 id="defaults-heading" className="text-sm font-semibold">
                  Default post settings
                </h3>
                <div className="mt-3 grid gap-3">
                  <div className="grid gap-1.5">
                    <Label htmlFor="default-visibility">Default visibility</Label>
                    <Input
                      id="default-visibility"
                      value={account.defaultSettings.visibility}
                      readOnly
                    />
                  </div>
                  <div className="grid gap-1.5">
                    <Label htmlFor="default-hashtags">Default hashtags</Label>
                    <Input
                      id="default-hashtags"
                      value={account.defaultSettings.hashtags}
                      onChange={(event) =>
                        onUpdateSettings(account.id, { hashtags: event.target.value })
                      }
                    />
                  </div>
                  {(
                    [
                      ["autoPublish", "Enable auto publish"],
                      ["aiOptimization", "Enable AI optimization"],
                      ["autoSchedule", "Enable auto schedule"],
                      ["urlTracking", "Enable URL tracking"],
                    ] as const
                  ).map(([key, label]) => (
                    <div
                      key={key}
                      className="flex items-center justify-between rounded-lg border px-3 py-2"
                    >
                      <Label htmlFor={`setting-${key}`}>{label}</Label>
                      <Switch
                        id={`setting-${key}`}
                        checked={account.defaultSettings[key]}
                        onCheckedChange={(checked) =>
                          onUpdateSettings(account.id, { [key]: checked === true })
                        }
                      />
                    </div>
                  ))}
                </div>
              </section>

              <div className="flex flex-wrap gap-2 border-t pt-4">
                {account.connectionStatus === "connected" ? (
                  <>
                    <SecondaryButton type="button" onClick={() => onReconnect(account.id)}>
                      Refresh
                    </SecondaryButton>
                    <DestructiveButton
                      type="button"
                      onClick={() => {
                        onDisconnect(account.id);
                        onOpenChange(false);
                      }}
                    >
                      <Unplug className="size-4" aria-hidden="true" /> Disconnect
                    </DestructiveButton>
                  </>
                ) : (
                  <PrimaryButton type="button" onClick={() => onReconnect(account.id)}>
                    <Link2 className="size-4" aria-hidden="true" /> Reconnect
                  </PrimaryButton>
                )}
              </div>
            </motion.div>
          </DrawerContent>
        ) : null}
      </AnimatePresence>
    </Dialog>
  );
}

export type ActivityTimelineProps = {
  events: readonly ActivityEvent[];
};

const EVENT_ICON = {
  connected: Link2,
  disconnected: Unplug,
  publish_success: CheckCircle2,
  publish_failed: XCircle,
  permission_changed: CheckCircle2,
} as const;

export function ActivityTimeline({ events }: ActivityTimelineProps): React.JSX.Element {
  return (
    <section aria-labelledby="activity-heading" className="bg-card rounded-xl border p-4">
      <h2 id="activity-heading" className="text-heading-3">
        Activity timeline
      </h2>
      <ol className="mt-4 grid gap-3">
        {events.map((event) => {
          const Icon = EVENT_ICON[event.type];
          return (
            <li key={event.id} className="bg-muted/20 flex gap-3 rounded-lg border p-3">
              <Icon className="text-muted-foreground mt-0.5 size-4 shrink-0" aria-hidden="true" />
              <div>
                <p className="text-sm font-semibold">{event.platformName}</p>
                <p className="text-muted-foreground text-sm">{event.message}</p>
                <time
                  className="text-muted-foreground mt-1 block text-xs"
                  dateTime={event.timestamp}
                >
                  {formatDate(event.timestamp, { dateStyle: "medium", timeStyle: "short" })}
                </time>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
