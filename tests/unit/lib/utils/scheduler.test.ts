import { describe, expect, it } from "vitest";

import {
  addDays,
  computeAnalytics,
  detectConflicts,
  filterPosts,
  getMonthGridDays,
  isSameDay,
  movePostToDay,
  postsForDay,
  reorderPosts,
  startOfMonth,
} from "@/lib/utils/scheduler";
import { scheduledPostFactory } from "@/tests/factories";

describe("scheduler utilities", () => {
  const reference = new Date("2026-08-15T12:00:00.000Z");

  it("builds month grids and day comparisons", () => {
    const grid = getMonthGridDays(reference);
    expect(grid.length % 7).toBe(0);
    expect(isSameDay(reference, new Date(reference))).toBe(true);
    expect(startOfMonth(reference).getDate()).toBe(1);
  });

  it("filters posts by search, platform, and status", () => {
    const posts = [
      scheduledPostFactory.build({ title: "Azure Launch", status: "scheduled" }),
      scheduledPostFactory.build({ title: "Weekly Digest", status: "draft", platforms: ["x"] }),
    ];

    expect(filterPosts(posts, { search: "azure", platform: "all", status: "all" })).toHaveLength(1);
    expect(filterPosts(posts, { search: "", platform: "x", status: "all" })).toHaveLength(1);
    expect(filterPosts(posts, { search: "", platform: "all", status: "draft" })).toHaveLength(1);
  });

  it("detects past schedules and missing content conflicts", () => {
    const posts = [
      scheduledPostFactory.build({
        id: "past-1",
        title: "Past Post",
        scheduledAt: "2020-01-01T10:00:00.000Z",
      }),
      scheduledPostFactory.build({
        id: "missing-1",
        title: "Empty Post",
        hasContent: false,
      }),
    ];

    const conflicts = detectConflicts(posts);
    expect(conflicts.some((item) => item.type === "past_schedule")).toBe(true);
    expect(conflicts.some((item) => item.type === "missing_content")).toBe(true);
  });

  it("detects duplicate platform conflicts within 30 minutes", () => {
    const posts = [
      scheduledPostFactory.build({
        id: "a",
        title: "Morning Update",
        scheduledAt: "2026-09-01T10:00:00.000Z",
        platforms: ["linkedin"],
      }),
      scheduledPostFactory.build({
        id: "b",
        title: "Morning Recap",
        scheduledAt: "2026-09-01T10:15:00.000Z",
        platforms: ["linkedin"],
      }),
    ];

    expect(detectConflicts(posts).some((item) => item.type === "duplicate_platform")).toBe(true);
  });

  it("computes analytics for the current week", () => {
    const posts = [
      scheduledPostFactory.build({ scheduledAt: reference.toISOString(), status: "published" }),
      scheduledPostFactory.build({
        scheduledAt: addDays(reference, 1).toISOString(),
        status: "scheduled",
      }),
    ];

    const analytics = computeAnalytics(posts, reference);
    expect(analytics.postsToday).toBeGreaterThanOrEqual(1);
    expect(analytics.successRate).toBeGreaterThan(0);
  });

  it("moves and reorders posts while preserving queue order", () => {
    const posts = [
      scheduledPostFactory.build({ id: "one", queueOrder: 1 }),
      scheduledPostFactory.build({ id: "two", queueOrder: 2 }),
      scheduledPostFactory.build({ id: "three", queueOrder: 3 }),
    ];
    const targetDay = new Date("2026-09-10T00:00:00.000Z");
    const moved = movePostToDay(posts[0]!, targetDay);
    expect(new Date(moved.scheduledAt).getDate()).toBe(10);

    const reordered = reorderPosts(posts, "three", "one");
    expect(reordered.map((post) => post.id)).toEqual(["three", "one", "two"]);
    expect(reordered.every((post, index) => post.queueOrder === index + 1)).toBe(true);
  });

  it("returns posts scheduled on a given day", () => {
    const day = new Date("2026-08-15T00:00:00.000Z");
    const posts = [
      scheduledPostFactory.build({ scheduledAt: "2026-08-15T09:00:00.000Z" }),
      scheduledPostFactory.build({ scheduledAt: "2026-08-16T09:00:00.000Z" }),
    ];
    expect(postsForDay(posts, day)).toHaveLength(1);
  });
});
