"use client";

import { RefreshCw } from "lucide-react";
import * as React from "react";

import { Alert, LiveRegion, Skeleton } from "@/components/feedback";
import { PageContainer, Stack } from "@/components/layout";
import { IconButton } from "@/components/buttons";
import { useDashboardData } from "@/hooks/use-dashboard-data";

import { AiSuggestionsPanel } from "./ai-suggestions-panel";
import { DashboardBottomModules } from "./dashboard-bottom-modules";
import { DashboardHeader } from "./dashboard-header";
import { DashboardStats } from "./dashboard-stats";
import { PublishingCalendarPanel } from "./publishing-calendar-panel";
import { RecentContentTable } from "./recent-content-table";

export function DashboardView(): React.JSX.Element {
  const [refreshKey, setRefreshKey] = React.useState(0);
  const {
    stats,
    suggestions,
    agenda,
    recentContent,
    recentActivity,
    platformHealth,
    storage,
    healthSummary,
    partial,
    warnings,
    offline,
    error,
    isLoading,
    isRefreshing,
    reload,
  } = useDashboardData(refreshKey);

  function refresh(): void {
    setRefreshKey((current) => current + 1);
    void reload();
  }

  if (isLoading) {
    return (
      <PageContainer>
        <Stack gap="lg">
          <Skeleton className="h-28 w-full rounded-xl" />
          <div className="tablet:grid-cols-2 wide:grid-cols-5 grid gap-4">
            {Array.from({ length: 5 }).map((_, index) => (
              <Skeleton key={index} className="h-32 rounded-xl" />
            ))}
          </div>
          <Skeleton className="h-96 w-full rounded-xl" />
        </Stack>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <Stack gap="lg">
        <LiveRegion politeness="polite">{error ?? (partial ? warnings[0] : null)}</LiveRegion>
        {(error || offline || partial) && (
          <Alert
            variant={error ? "danger" : offline ? "warning" : "info"}
            title={error ? "Dashboard error" : offline ? "Offline mode" : "Partial dashboard data"}
            action={
              <IconButton
                label="Refresh dashboard"
                icon={<RefreshCw className={isRefreshing ? "animate-spin" : ""} aria-hidden="true" />}
                onClick={refresh}
              />
            }
          >
            {error ??
              (offline
                ? "Unable to reach the backend. Showing the last available dashboard state."
                : warnings.join(" "))}
          </Alert>
        )}

        <DashboardHeader
          healthSummary={healthSummary}
          onRefresh={refresh}
          isRefreshing={isRefreshing}
        />
        <DashboardStats stats={stats} />

        <div className="desktop:grid-cols-12 desktop:items-start grid gap-4">
          <div className="desktop:col-span-8">
            <AiSuggestionsPanel suggestions={suggestions} />
          </div>
          <div className="desktop:col-span-4">
            <PublishingCalendarPanel agenda={agenda} />
          </div>
        </div>

        <RecentContentTable rows={recentContent} />
        <DashboardBottomModules
          recentActivity={recentActivity}
          platformHealth={platformHealth}
          storage={storage}
        />
      </Stack>
    </PageContainer>
  );
}
