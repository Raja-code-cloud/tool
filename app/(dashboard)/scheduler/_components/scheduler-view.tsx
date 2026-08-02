"use client";

import { motion } from "framer-motion";
import { Plus } from "lucide-react";
import dynamic from "next/dynamic";
import { useMemo, useRef } from "react";

import { LiveRegion } from "@/components/feedback";
import { PageContainer, PageHeader } from "@/components/layout";
import { Button } from "@/components/ui";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";
import { cn } from "@/lib/utils/cn";

import { AnalyticsWidget } from "./analytics-widget";
import { CalendarWorkspace } from "./calendar-workspace";
import { ConflictAlerts } from "./conflict-alerts";
import { DetailsPanel } from "./details-panel";
import { NotificationsBar } from "./notifications-bar";
import { QueuePanel } from "./queue-panel";
import { SchedulerEmptyState } from "./scheduler-empty-states";
import { SchedulerToolbar } from "./scheduler-toolbar";
import type { MobilePanel } from "./types";
import { useSchedulerState } from "./use-scheduler-state";

const QuickScheduleDialog = dynamic(() =>
  import("./quick-schedule-dialog").then((module) => module.QuickScheduleDialog),
);

const MOBILE_TABS: readonly { id: MobilePanel; label: string }[] = [
  { id: "queue", label: "Queue" },
  { id: "calendar", label: "Calendar" },
  { id: "details", label: "Details" },
];

export function SchedulerView(): React.JSX.Element {
  const state = useSchedulerState();
  const mobileTabRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const moveMobileTab = (from: number, delta: number): void => {
    const next = MOBILE_TABS[(from + delta + MOBILE_TABS.length) % MOBILE_TABS.length];
    if (next) {
      state.setMobilePanel(next.id);
      mobileTabRefs.current[(from + delta + MOBILE_TABS.length) % MOBILE_TABS.length]?.focus();
    }
  };

  const moveMobileTabToEdge = (edge: "start" | "end"): void => {
    const target = edge === "start" ? MOBILE_TABS[0] : MOBILE_TABS[MOBILE_TABS.length - 1];
    const targetIndex = edge === "start" ? 0 : MOBILE_TABS.length - 1;
    if (target) {
      state.setMobilePanel(target.id);
      mobileTabRefs.current[targetIndex]?.focus();
    }
  };

  const conflictPostIds = useMemo(
    () => new Set(state.conflicts.flatMap((conflict) => conflict.postIds)),
    [state.conflicts],
  );

  const selectedHasConflict = state.selectedId ? conflictPostIds.has(state.selectedId) : false;
  const showEmptySearch =
    state.filteredPosts.length === 0 &&
    (state.filters.search || state.filters.platform !== "all" || state.filters.status !== "all");

  return (
    <PageContainer className="pb-24">
      <div className="grid gap-5">
        <PageHeader
          title="Scheduler"
          description="Publishing control center — schedule, queue, and monitor content across platforms."
        />

        <AnalyticsWidget analytics={state.analytics} />
        <NotificationsBar notifications={state.notifications} />
        <ConflictAlerts conflicts={state.conflicts} />

        <SchedulerToolbar
          view={state.view}
          onViewChange={state.setView}
          filters={state.filters}
          onFiltersChange={state.patchFilters}
          timezone={state.timezone}
          onTimezoneChange={state.setTimezone}
          onToday={state.goToday}
          onPrevious={() => state.navigate(-1)}
          onNext={() => state.navigate(1)}
          onRefresh={state.refresh}
          isRefreshing={state.loadingArea === "calendar"}
        />

        <div
          className="bg-card flex gap-1 rounded-lg border p-1 lg:hidden"
          role="tablist"
          aria-label="Scheduler panels"
        >
          {MOBILE_TABS.map((tab, index) => (
            <Button
              key={tab.id}
              ref={(node) => {
                mobileTabRefs.current[index] = node;
              }}
              type="button"
              role="tab"
              id={`tab-${tab.id}`}
              aria-controls={`panel-${tab.id}`}
              aria-selected={state.mobilePanel === tab.id}
              tabIndex={state.mobilePanel === tab.id ? 0 : -1}
              variant={state.mobilePanel === tab.id ? "secondary" : "ghost"}
              className="flex-1"
              onClick={() => state.setMobilePanel(tab.id)}
              onKeyDown={(event) => {
                if (event.key === "ArrowRight") {
                  event.preventDefault();
                  moveMobileTab(index, 1);
                }
                if (event.key === "ArrowLeft") {
                  event.preventDefault();
                  moveMobileTab(index, -1);
                }
                if (event.key === "Home") {
                  event.preventDefault();
                  moveMobileTabToEdge("start");
                }
                if (event.key === "End") {
                  event.preventDefault();
                  moveMobileTabToEdge("end");
                }
              }}
            >
              {tab.label}
            </Button>
          ))}
        </div>

        {showEmptySearch ? (
          <SchedulerEmptyState variant="no-search" />
        ) : (
          <div className="grid gap-5 lg:grid-cols-2 xl:grid-cols-[minmax(260px,300px)_minmax(0,1fr)_minmax(280px,320px)]">
            <div
              role="tabpanel"
              id="panel-queue"
              aria-labelledby="tab-queue"
              className={cn(
                "min-w-0 lg:col-span-2 xl:col-span-1",
                state.mobilePanel !== "queue" && "max-lg:hidden",
              )}
            >
              <QueuePanel
                posts={state.filteredPosts}
                activeSection={state.activeQueueSection}
                onSectionChange={state.setActiveQueueSection}
                selectedId={state.selectedId}
                onSelect={state.selectPost}
                onReorder={state.reorderQueue}
                draggedId={state.draggedId}
                onDragStart={state.setDraggedId}
                onDragEnd={() => state.setDraggedId(null)}
                conflictPostIds={conflictPostIds}
                isLoading={state.loadingArea === "queue"}
                timezone={state.timezone}
              />
            </div>

            <div
              role="tabpanel"
              id="panel-calendar"
              aria-labelledby="tab-calendar"
              className={cn("min-w-0", state.mobilePanel !== "calendar" && "max-lg:hidden")}
            >
              <CalendarWorkspace
                view={state.view}
                data={{
                  currentDate: state.currentDate,
                  posts: state.filteredPosts,
                  timezone: state.timezone,
                }}
                selection={{ selectedId: state.selectedId, onSelect: state.selectPost }}
                dragActions={{
                  draggedId: state.draggedId,
                  onReschedule: state.reschedulePost,
                  onDragStart: state.setDraggedId,
                  onDragEnd: () => state.setDraggedId(null),
                }}
                isLoading={state.loadingArea === "calendar"}
                onQuickAdd={() => state.setQuickScheduleOpen(true)}
              />
            </div>

            <div
              role="tabpanel"
              id="panel-details"
              aria-labelledby="tab-details"
              className={cn("min-w-0", state.mobilePanel !== "details" && "max-lg:hidden")}
            >
              <DetailsPanel
                post={state.selectedPost}
                isLoading={state.loadingArea === "details"}
                timezone={state.timezone}
                hasConflict={selectedHasConflict}
                onEdit={() => state.setQuickScheduleOpen(true)}
                onDuplicate={() => state.selectedId && state.duplicatePost(state.selectedId)}
                onCancel={() => state.selectedId && state.cancelPost(state.selectedId)}
                onDelete={() => state.selectedId && state.deletePost(state.selectedId)}
                onPublishNow={() => state.selectedId && state.publishNow(state.selectedId)}
                onReschedule={() => state.setQuickScheduleOpen(true)}
              />
            </div>
          </div>
        )}
      </div>

      <LiveRegion>
        {state.selectedPost ? `Selected: ${state.selectedPost.title}` : "No event selected"}
      </LiveRegion>

      <motion.button
        type="button"
        className="bg-primary text-primary-foreground focus-visible:ring-ring fixed right-6 bottom-6 z-40 grid size-14 place-items-center rounded-full shadow-lg hover:brightness-110 focus-visible:ring-2 focus-visible:outline-none"
        aria-label="Create schedule"
        onClick={() => state.setQuickScheduleOpen(true)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.97 }}
        transition={{ duration: MOTION_DURATION.hover, ease: MOTION_EASING.enter }}
      >
        <Plus className="size-6" aria-hidden="true" />
      </motion.button>

      {state.quickScheduleOpen && (
        <QuickScheduleDialog
          open
          onOpenChange={state.setQuickScheduleOpen}
          defaults={state.defaultQuickSchedule}
          onSubmit={state.createSchedule}
        />
      )}
    </PageContainer>
  );
}
