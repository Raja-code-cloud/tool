"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { useToast } from "@/hooks/use-toast";
import type { PlatformId } from "@/lib/domain/platform";
import type {
  CalendarView,
  QueueSection,
  ScheduledPost,
  SchedulerNotification,
} from "@/lib/domain/scheduler";
import { schedulerErrorMessage } from "@/lib/scheduler/errors";
import { toRequestedLocalAt } from "@/lib/scheduler/mappers";
import { isBackendSchedulerEnabled, schedulerService } from "@/lib/services";
import {
  computeAnalytics,
  detectConflicts,
  filterPosts,
  movePostToDay,
  reorderPosts,
  type SchedulerFilters,
} from "@/lib/utils/scheduler";

import {
  DEFAULT_QUICK_SCHEDULE,
  REFERENCE_DATE,
  type LoadingArea,
  type MobilePanel,
  type QuickScheduleForm,
} from "./types";

async function loadInitialPosts(): Promise<readonly ScheduledPost[]> {
  return schedulerService.listPosts({ sort: "-scheduledFor", limit: 100 });
}

export function useSchedulerState() {
  const { toast } = useToast();
  const [posts, setPosts] = useState<readonly ScheduledPost[]>([]);
  const [view, setView] = useState<CalendarView>("month");
  const [currentDate, setCurrentDate] = useState(REFERENCE_DATE);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [activeQueueSection, setActiveQueueSection] = useState<QueueSection>("upcoming");
  const [timezone, setTimezone] = useState("America/New_York");
  const [filters, setFilters] = useState<SchedulerFilters>({
    search: "",
    platform: "all",
    status: "all",
  });
  const [mobilePanel, setMobilePanel] = useState<MobilePanel>("calendar");
  const [quickScheduleOpen, setQuickScheduleOpen] = useState(false);
  const [loadingArea, setLoadingArea] = useState<LoadingArea>(null);
  const [notifications, setNotifications] = useState<readonly SchedulerNotification[]>(() =>
    schedulerService.listNotifications(),
  );
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const initialPosts = await loadInitialPosts();
        if (!cancelled) {
          setPosts(initialPosts);
          setSelectedId(initialPosts[0]?.id ?? null);
        }
      } catch (error) {
        if (!cancelled) {
          toast({
            title: "Unable to load schedules",
            description: schedulerErrorMessage(error),
          });
        }
      } finally {
        if (!cancelled) setIsBootstrapping(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [toast]);

  const filteredPosts = useMemo(() => filterPosts(posts, filters), [posts, filters]);
  const conflicts = useMemo(() => detectConflicts(posts), [posts]);
  const analytics = useMemo(() => computeAnalytics(posts, REFERENCE_DATE), [posts]);
  const selectedPost = useMemo(
    () => posts.find((post) => post.id === selectedId) ?? null,
    [posts, selectedId],
  );

  const reloadPosts = useCallback(async () => {
    const nextPosts = await schedulerService.listPosts({ sort: "-scheduledFor", limit: 100 });
    setPosts(nextPosts);
    return nextPosts;
  }, []);

  const simulateLoad = useCallback(
    async (area: LoadingArea, action: () => void | Promise<void>) => {
      setLoadingArea(area);
      try {
        await action();
      } finally {
        setLoadingArea(null);
      }
    },
    [],
  );

  const refresh = useCallback(() => {
    void simulateLoad("calendar", async () => {
      try {
        await reloadPosts();
        toast({
          title: "Schedule refreshed",
          description: "Publishing queue and calendar are up to date.",
        });
      } catch (error) {
        toast({
          title: "Refresh failed",
          description: schedulerErrorMessage(error),
        });
      }
    });
  }, [reloadPosts, simulateLoad, toast]);

  const goToday = useCallback(() => setCurrentDate(REFERENCE_DATE), []);

  const navigate = useCallback(
    (direction: -1 | 1) => {
      setCurrentDate((prev) => {
        const next = new Date(prev);
        if (view === "month") next.setMonth(next.getMonth() + direction);
        else if (view === "week") next.setDate(next.getDate() + direction * 7);
        else next.setDate(next.getDate() + direction);
        return next;
      });
    },
    [view],
  );

  const selectPost = useCallback((id: string) => {
    setSelectedId(id);
    setMobilePanel("details");
  }, []);

  const updatePost = useCallback((id: string, patch: Partial<ScheduledPost>) => {
    setPosts((prev) => prev.map((post) => (post.id === id ? { ...post, ...patch } : post)));
  }, []);

  const reschedulePost = useCallback(
    (id: string, day: Date) => {
      void simulateLoad("calendar", async () => {
        const post = posts.find((entry) => entry.id === id);
        if (!post) return;

        if (isBackendSchedulerEnabled) {
          try {
            const moved = movePostToDay(post, day);
            const localDate = moved.scheduledAt.slice(0, 10);
            const localTime = new Date(moved.scheduledAt).toISOString().slice(11, 19);
            const updated = await schedulerService.updateSchedule(post.id, post.version, {
              requestedLocalAt: toRequestedLocalAt(localDate, localTime),
              timeZone: post.timezone,
            });
            setPosts((prev) => prev.map((entry) => (entry.id === id ? updated : entry)));
            toast({ title: "Post rescheduled", description: "Schedule updated on the server." });
            return;
          } catch (error) {
            toast({
              title: "Reschedule failed",
              description: schedulerErrorMessage(error),
            });
            return;
          }
        }

        setPosts((prev) =>
          prev.map((entry) => (entry.id === id ? movePostToDay(entry, day) : entry)),
        );
        toast({ title: "Post rescheduled", description: "Drag-and-drop schedule updated." });
      });
    },
    [posts, simulateLoad, toast],
  );

  const reorderQueue = useCallback((fromId: string, toId: string) => {
    setPosts((prev) => reorderPosts([...prev], fromId, toId));
  }, []);

  const cancelPost = useCallback(
    (id: string) => {
      void simulateLoad("details", async () => {
        const post = posts.find((entry) => entry.id === id);
        if (!post) return;

        try {
          const updated = await schedulerService.cancelSchedule(post.id, post.version);
          setPosts((prev) => prev.map((entry) => (entry.id === id ? updated : entry)));
          toast({ title: "Post cancelled", description: "The schedule entry was cancelled." });
        } catch (error) {
          toast({
            title: "Cancel failed",
            description: schedulerErrorMessage(error),
          });
        }
      });
    },
    [posts, simulateLoad, toast],
  );

  const deletePost = useCallback(
    (id: string) => {
      void cancelPost(id);
    },
    [cancelPost],
  );

  const duplicatePost = useCallback(
    (id: string) => {
      void simulateLoad("details", async () => {
        const source = posts.find((post) => post.id === id);
        if (!source) return;

        if (isBackendSchedulerEnabled) {
          toast({
            title: "Duplicate unavailable",
            description:
              "Create a new publication target before scheduling a duplicate on the backend.",
          });
          return;
        }

        const copy: ScheduledPost = {
          ...source,
          id: `sch-${Date.now()}`,
          version: 1,
          title: `${source.title} (copy)`,
          status: "draft",
          queueOrder: posts.length + 1,
        };
        setPosts((prev) => [...prev, copy]);
        setSelectedId(copy.id);
        toast({ title: "Post duplicated", description: "A draft copy was created." });
      });
    },
    [posts, simulateLoad, toast],
  );

  const publishNow = useCallback(
    (id: string) => {
      void simulateLoad("details", async () => {
        const post = posts.find((entry) => entry.id === id);
        if (!post) return;

        if (isBackendSchedulerEnabled) {
          if (!post.publicationId) {
            toast({
              title: "Publish unavailable",
              description: "This schedule is not linked to a publication aggregate.",
            });
            return;
          }

          try {
            updatePost(id, { status: "publishing" });
            await schedulerService.dispatchPublication(post.publicationId, post.version, [
              post.publicationTargetId,
            ]);
            const refreshed = await reloadPosts();
            const latest = refreshed.find((entry) => entry.id === id);
            if (latest) updatePost(id, latest);
            setNotifications((prev) => [
              {
                id: `n-${Date.now()}`,
                message: "Publication dispatch accepted.",
                variant: "success",
                timestamp: new Date().toISOString(),
              },
              ...prev,
            ]);
            toast({
              title: "Published",
              description: "Dispatch accepted by the publishing queue.",
            });
          } catch (error) {
            updatePost(id, { status: post.status });
            toast({
              title: "Publish failed",
              description: schedulerErrorMessage(error),
            });
          }
          return;
        }

        updatePost(id, { status: "publishing" });
        window.setTimeout(() => {
          updatePost(id, { status: "published" });
          setNotifications((prev) => [
            {
              id: `n-${Date.now()}`,
              message: "Post published successfully (mock).",
              variant: "success",
              timestamp: new Date().toISOString(),
            },
            ...prev,
          ]);
          toast({ title: "Published", description: "Mock publish completed." });
        }, 1200);
      });
    },
    [posts, reloadPosts, simulateLoad, toast, updatePost],
  );

  const createSchedule = useCallback(
    (form: QuickScheduleForm) => {
      void simulateLoad("queue", async () => {
        if (isBackendSchedulerEnabled) {
          if (!form.publicationTargetId) {
            toast({
              title: "Publication target required",
              description:
                "Scheduling requires an approved publication target ID from the publishing workflow.",
            });
            return;
          }

          try {
            const created = await schedulerService.createSchedule({
              publicationTargetId: form.publicationTargetId,
              requestedLocalAt: toRequestedLocalAt(form.date, form.time),
              timeZone: form.timezone,
              priority: form.priority,
            });
            setPosts((prev) => [...prev, created]);
            setSelectedId(created.id);
            setQuickScheduleOpen(false);
            setNotifications((prev) => [
              {
                id: `n-${Date.now()}`,
                message: `${form.platform} post scheduled successfully.`,
                variant: "success",
                timestamp: new Date().toISOString(),
              },
              ...prev,
            ]);
            toast({
              title: "Schedule created",
              description: `"${created.title}" was added to the queue.`,
            });
          } catch (error) {
            toast({
              title: "Schedule creation failed",
              description: schedulerErrorMessage(error),
            });
          }
          return;
        }

        const scheduledAt = new Date(`${form.date}T${form.time}:00`).toISOString();
        const newPost: ScheduledPost = {
          id: `sch-${Date.now()}`,
          version: 1,
          publicationTargetId: `target-${Date.now()}`,
          title: form.title,
          platforms: [form.platform as PlatformId],
          scheduledAt,
          timezone: form.timezone,
          status: "scheduled",
          priority: form.priority,
          thumbnailHue: Math.floor(Math.random() * 360),
          aiVersion: "v1.0",
          approvalStatus: "pending",
          queueOrder: posts.length + 1,
          hasContent: true,
        };
        setPosts((prev) => [...prev, newPost]);
        setSelectedId(newPost.id);
        setQuickScheduleOpen(false);
        setNotifications((prev) => [
          {
            id: `n-${Date.now()}`,
            message: `${form.platform} post scheduled successfully.`,
            variant: "success",
            timestamp: new Date().toISOString(),
          },
          ...prev,
        ]);
        toast({
          title: "Schedule created",
          description: `"${form.title}" was added to the queue.`,
        });
      });
    },
    [posts.length, simulateLoad, toast],
  );

  const patchFilters = useCallback((patch: Partial<SchedulerFilters>) => {
    setFilters((prev) => ({ ...prev, ...patch }));
  }, []);

  return {
    posts,
    filteredPosts,
    view,
    setView,
    currentDate,
    setCurrentDate,
    selectedId,
    selectedPost,
    selectPost,
    activeQueueSection,
    setActiveQueueSection,
    timezone,
    setTimezone,
    filters,
    patchFilters,
    mobilePanel,
    setMobilePanel,
    quickScheduleOpen,
    setQuickScheduleOpen,
    loadingArea: loadingArea ?? (isBootstrapping ? "calendar" : null),
    notifications,
    conflicts,
    analytics,
    draggedId,
    setDraggedId,
    refresh,
    goToday,
    navigate,
    reschedulePost,
    reorderQueue,
    cancelPost,
    deletePost,
    duplicatePost,
    publishNow,
    createSchedule,
    updatePost,
    defaultQuickSchedule: DEFAULT_QUICK_SCHEDULE,
  };
}
