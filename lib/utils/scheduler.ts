import type { PlatformId } from "@/lib/domain/platform";
import type { ScheduledPost, ScheduleStatus } from "@/lib/domain/scheduler";

export type ScheduleConflict = {
  readonly id: string;
  readonly type: "time_collision" | "duplicate_platform" | "past_schedule" | "missing_content";
  readonly message: string;
  readonly postIds: readonly string[];
};

export function startOfDay(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

export function startOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

export function endOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0);
}

export function addDays(date: Date, days: number): Date {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

export function addMonths(date: Date, months: number): Date {
  const next = new Date(date);
  next.setMonth(next.getMonth() + months);
  return next;
}

export function addWeeks(date: Date, weeks: number): Date {
  return addDays(date, weeks * 7);
}

export function isSameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

export function isSameMonth(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth();
}

export function isToday(date: Date, reference = new Date()): boolean {
  return isSameDay(date, reference);
}

export function isWeekend(date: Date): boolean {
  const day = date.getDay();
  return day === 0 || day === 6;
}

export function getMonthGridDays(reference: Date): readonly Date[] {
  const start = startOfMonth(reference);
  const end = endOfMonth(reference);
  const gridStart = addDays(start, -start.getDay());
  const gridEnd = addDays(end, 6 - end.getDay());
  const days: Date[] = [];
  let current = gridStart;
  while (current <= gridEnd) {
    days.push(new Date(current));
    current = addDays(current, 1);
  }
  return days;
}

export function getWeekDays(reference: Date): readonly Date[] {
  const start = addDays(reference, -reference.getDay());
  return Array.from({ length: 7 }, (_, index) => addDays(start, index));
}

export function formatScheduleTime(iso: string, timezone: string): string {
  return new Intl.DateTimeFormat(undefined, {
    hour: "numeric",
    minute: "2-digit",
    timeZone: timezone,
  }).format(new Date(iso));
}

export function formatScheduleDate(iso: string, timezone: string): string {
  return new Intl.DateTimeFormat(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    timeZone: timezone,
  }).format(new Date(iso));
}

export function formatMonthYear(date: Date): string {
  return new Intl.DateTimeFormat(undefined, { month: "long", year: "numeric" }).format(date);
}

export type SchedulerFilters = {
  search: string;
  platform: PlatformId | "all";
  status: ScheduleStatus | "all";
};

export function filterPosts(
  posts: readonly ScheduledPost[],
  filters: SchedulerFilters,
): ScheduledPost[] {
  const query = filters.search.trim().toLowerCase();
  return posts.filter((post) => {
    if (filters.status !== "all" && post.status !== filters.status) return false;
    if (filters.platform !== "all" && !post.platforms.includes(filters.platform)) return false;
    if (query && !post.title.toLowerCase().includes(query)) return false;
    return true;
  });
}

export function postsForDay(posts: readonly ScheduledPost[], day: Date): ScheduledPost[] {
  return posts.filter((post) => isSameDay(new Date(post.scheduledAt), day));
}

export function detectConflicts(posts: readonly ScheduledPost[]): ScheduleConflict[] {
  const conflicts: ScheduleConflict[] = [];
  const now = new Date();

  posts.forEach((post) => {
    if (new Date(post.scheduledAt) < now && ["scheduled", "ready", "draft"].includes(post.status)) {
      conflicts.push({
        id: `past-${post.id}`,
        type: "past_schedule",
        message: `"${post.title}" is scheduled in the past.`,
        postIds: [post.id],
      });
    }
    if (!post.hasContent && post.status !== "published" && post.status !== "cancelled") {
      conflicts.push({
        id: `missing-${post.id}`,
        type: "missing_content",
        message: `"${post.title}" is missing content assets.`,
        postIds: [post.id],
      });
    }
  });

  for (let i = 0; i < posts.length; i += 1) {
    for (let j = i + 1; j < posts.length; j += 1) {
      const a = posts[i];
      const b = posts[j];
      if (!a || !b) continue;
      const timeA = new Date(a.scheduledAt).getTime();
      const timeB = new Date(b.scheduledAt).getTime();
      if (
        Math.abs(timeA - timeB) < 30 * 60 * 1000 &&
        a.status !== "cancelled" &&
        b.status !== "cancelled"
      ) {
        const shared = a.platforms.filter((p) => b.platforms.includes(p));
        if (shared.length > 0) {
          conflicts.push({
            id: `dup-${a.id}-${b.id}`,
            type: "duplicate_platform",
            message: `${shared.join(", ")} conflict between "${a.title}" and "${b.title}".`,
            postIds: [a.id, b.id],
          });
        } else if (timeA === timeB) {
          conflicts.push({
            id: `time-${a.id}-${b.id}`,
            type: "time_collision",
            message: `"${a.title}" and "${b.title}" are scheduled at the same time.`,
            postIds: [a.id, b.id],
          });
        }
      }
    }
  }

  return conflicts;
}

export type SchedulerAnalytics = {
  postsToday: number;
  postsThisWeek: number;
  scheduled: number;
  missed: number;
  failed: number;
  successRate: number;
};

export function computeAnalytics(
  posts: readonly ScheduledPost[],
  reference = new Date(),
): SchedulerAnalytics {
  const todayStart = startOfDay(reference);
  const weekStart = addDays(todayStart, -todayStart.getDay());
  const weekEnd = addDays(weekStart, 7);
  const now = reference;

  let postsToday = 0;
  let postsThisWeek = 0;
  let scheduled = 0;
  let missed = 0;
  let failed = 0;
  let published = 0;

  posts.forEach((post) => {
    const date = new Date(post.scheduledAt);
    if (isSameDay(date, todayStart)) postsToday += 1;
    if (date >= weekStart && date < weekEnd) postsThisWeek += 1;
    if (post.status === "scheduled" || post.status === "ready") scheduled += 1;
    if (post.status === "failed") failed += 1;
    if (post.status === "published") published += 1;
    if (date < now && ["scheduled", "ready", "failed"].includes(post.status)) missed += 1;
  });

  const total = published + failed;
  const successRate = total > 0 ? Math.round((published / total) * 100) : 100;

  return { postsToday, postsThisWeek, scheduled, missed, failed, successRate };
}

export function movePostToDay(post: ScheduledPost, day: Date): ScheduledPost {
  const current = new Date(post.scheduledAt);
  const next = new Date(day);
  next.setHours(current.getHours(), current.getMinutes(), 0, 0);
  return { ...post, scheduledAt: next.toISOString() };
}

export function reorderPosts(
  posts: ScheduledPost[],
  fromId: string,
  toId: string,
): ScheduledPost[] {
  const sorted = [...posts].sort((a, b) => a.queueOrder - b.queueOrder);
  const fromIndex = sorted.findIndex((post) => post.id === fromId);
  const toIndex = sorted.findIndex((post) => post.id === toId);
  if (fromIndex < 0 || toIndex < 0 || fromIndex === toIndex) return posts;
  const [moved] = sorted.splice(fromIndex, 1);
  if (!moved) return posts;
  sorted.splice(toIndex, 0, moved);
  return sorted.map((post, index) => ({ ...post, queueOrder: index + 1 }));
}
