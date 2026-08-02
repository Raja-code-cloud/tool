"use client";

import { motion } from "framer-motion";
import dynamic from "next/dynamic";

import { LiveRegion, Skeleton } from "@/components/feedback";
import { PageContainer, PageHeader, Stack } from "@/components/layout";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";

import { AccountDetailsDrawer, ActivityTimeline } from "./account-details-drawer";
import { AccountGrid } from "./account-grid";
import { OverviewCards } from "./overview-cards";
import { SocialAccountsEmptyState, SocialAccountsToolbar } from "./social-accounts-toolbar";
import { useSocialAccountsState } from "./use-social-accounts-state";

const ConnectAccountDialog = dynamic(() =>
  import("./connect-account-dialog").then((module) => module.ConnectAccountDialog),
);

export function SocialAccountsView(): React.JSX.Element {
  const state = useSocialAccountsState();

  const handleRefreshAccount = (id: string): void => {
    void state.reconnectAccount(id);
  };

  return (
    <PageContainer className="pb-8">
      <Stack gap="lg">
        <PageHeader
          title="Social accounts"
          description="Connect and manage publishing platforms."
        />

        <SocialAccountsToolbar
          search={state.search}
          onSearchChange={state.setSearch}
          filter={state.filter}
          onFilterChange={state.setFilter}
          onConnect={() => state.setConnectOpen(true)}
          onRefresh={state.refresh}
          isRefreshing={state.isRefreshing}
        />

        {state.isLoading || state.isRefreshing ? (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            {Array.from({ length: 5 }, (_, index) => (
              <Skeleton key={index} className="h-28 rounded-xl" />
            ))}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: MOTION_DURATION.page, ease: MOTION_EASING.enter }}
          >
            <OverviewCards overview={state.overview} />
          </motion.div>
        )}

        {state.loadError ? (
          <div
            className="bg-destructive/10 text-destructive rounded-xl border border-destructive/20 p-4 text-sm"
            role="alert"
          >
            {state.loadError}
          </div>
        ) : null}

        {!state.isLoading && state.overview.connected === 0 && state.filter === "all" && !state.search.trim() ? (
          <SocialAccountsEmptyState onConnect={() => state.setConnectOpen(true)} />
        ) : state.showEmpty ? (
          <div
            className="bg-card text-muted-foreground rounded-xl border p-8 text-center text-sm"
            role="status"
          >
            No accounts match your search or filters.
          </div>
        ) : (
          <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(280px,320px)]">
            <AccountGrid
              accounts={state.activeAccounts}
              comingSoon={state.comingSoonAccounts}
              actions={{
                onOpen: state.openAccount,
                onReconnect: state.reconnectAccount,
                onDisconnect: state.disconnectAccount,
                onRefresh: handleRefreshAccount,
                onTogglePublishing: state.togglePublishing,
              }}
            />
            <ActivityTimeline events={state.activityEvents} />
          </div>
        )}
      </Stack>

      <LiveRegion>
        {state.selectedAccount ? `Viewing ${state.selectedAccount.accountName}` : "Social accounts"}
      </LiveRegion>

      <AccountDetailsDrawer
        account={state.selectedAccount}
        open={state.drawerOpen}
        onOpenChange={state.setDrawerOpen}
        onDisconnect={state.disconnectAccount}
        onReconnect={state.reconnectAccount}
        onTogglePublishing={state.togglePublishing}
        onUpdateSettings={state.updateSettings}
      />

      {state.connectOpen && (
        <ConnectAccountDialog
          open
          onOpenChange={state.setConnectOpen}
          onConnect={state.connectAccount}
        />
      )}
    </PageContainer>
  );
}
