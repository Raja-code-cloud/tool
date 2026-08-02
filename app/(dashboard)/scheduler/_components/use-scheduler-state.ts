"use client";

import { useCallback, useMemo, useState } from "react";

import { useToast } from "@/hooks/use-toast";
import type { PlatformId } from "@/lib/domain/platform";
import type {
  CalendarView,
  QueueSection,
  ScheduledPost,
  SchedulerNotification,
} from "@/lib/domain/scheduler";
import { schedulerService } from "@/lib/services";
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

export function useSchedulerState() {
  const { toast } = useToast();
  const [posts, setPosts] = useState<readonly ScheduledPost[]>(() => schedulerService.listPosts());
  const [view, setView] = useState<CalendarView>("month");
  const [currentDate, setCurrentDate] = useState(REFERENCE_DATE);
  const [selectedId, setSelectedId] = useState<string | null>("sch-1");
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

  const filteredPosts = useMemo(() => filterPosts(posts, filters), [posts, filters]);
  const conflicts = useMemo(() => detectConflicts(posts), [posts]);
  const analytics = useMemo(() => computeAnalytics(posts, REFERENCE_DATE), [posts]);
  const selectedPost = useMemo(
    () => posts.find((post) => post.id === selectedId) ?? null,
    [posts, selectedId],
  );

  const simulateLoad = useCallback(async (area: LoadingArea, action: () => void) => {
    setLoadingArea(area);
    await new Promise((resolve) => window.setTimeout(resolve, 400));
    action();
    setLoadingArea(null);
  }, []);

  const refresh = useCallback(() => {
    void simulateLoad("calendar", () => {
      toast({
        title: "Schedule refreshed",
        description: "Publishing queue and calendar are up to date.",
      });
    });
  }, [simulateLoad, toast]);

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
      setPosts((prev) => prev.map((post) => (post.id === id ? movePostToDay(post, day) : post)));
      toast({ title: "Post rescheduled", description: "Drag-and-drop schedule updated." });
    },
    [toast],
  );

  const reorderQueue = useCallback((fromId: string, toId: string) => {
    setPosts((prev) => reorderPosts([...prev], fromId, toId));
  }, []);

  const cancelPost = useCallback(
    (id: string) => {
      updatePost(id, { status: "cancelled" });
      toast({ title: "Post cancelled", description: "The schedule entry was cancelled." });
    },
    [toast, updatePost],
  );

  const deletePost = useCallback(
    (id: string) => {
      setPosts((prev) => prev.filter((post) => post.id !== id));
      setSelectedId(null);
      toast({ title: "Post deleted", description: "Schedule entry removed." });
    },
    [toast],
  );

  const duplicatePost = useCallback(
    (id: string) => {
      const source = posts.find((post) => post.id === id);
      if (!source) return;
      const copy: ScheduledPost = {
        ...source,
        id: `sch-${Date.now()}`,
        title: `${source.title} (copy)`,
        status: "draft",
        queueOrder: posts.length + 1,
      };
      setPosts((prev) => [...prev, copy]);
      setSelectedId(copy.id);
      toast({ title: "Post duplicated", description: "A draft copy was created." });
    },
    [posts, toast],
  );

  const publishNow = useCallback(
    (id: string) => {
      void simulateLoad("details", () => {
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
    [simulateLoad, toast, updatePost],
  );

  const createSchedule = useCallback(
    (form: QuickScheduleForm) => {
      const scheduledAt = new Date(`${form.date}T${form.time}:00`).toISOString();
      const newPost: ScheduledPost = {
        id: `sch-${Date.now()}`,
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
      toast({ title: "Schedule created", description: `"${form.title}" was added to the queue.` });
    },
    [posts.length, toast],
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
    loadingArea,
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
