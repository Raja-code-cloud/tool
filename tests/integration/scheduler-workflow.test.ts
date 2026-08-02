import { describe, expect, it } from "vitest";

import { SCHEDULED_POSTS } from "@/constants/scheduler";
import {
  computeAnalytics,
  detectConflicts,
  filterPosts,
  reorderPosts,
} from "@/lib/utils/scheduler";
import { scheduledPostFactory } from "@/tests/factories";

describe("scheduler workflow", () => {
  it("filters the queue and computes analytics from mock schedule data", () => {
    const filtered = filterPosts(SCHEDULED_POSTS, {
      search: "",
      platform: "linkedin",
      status: "all",
    });
    const analytics = computeAnalytics(SCHEDULED_POSTS, new Date("2026-08-15T12:00:00.000Z"));

    expect(filtered.length).toBeGreaterThan(0);
    expect(analytics.scheduled).toBeGreaterThan(0);
  });

  it("reorders queue items and surfaces scheduling conflicts", () => {
    const posts = [
      scheduledPostFactory.build({ id: "a", queueOrder: 1 }),
      scheduledPostFactory.build({ id: "b", queueOrder: 2 }),
      scheduledPostFactory.build({ id: "c", queueOrder: 3 }),
    ];
    const reordered = reorderPosts(posts, "c", "a");
    expect(reordered.map((post) => post.id)).toEqual(["c", "a", "b"]);

    const conflicts = detectConflicts([
      ...posts,
      scheduledPostFactory.build({
        id: "conflict",
        title: "Overlap",
        scheduledAt: posts[0]!.scheduledAt,
        platforms: posts[0]!.platforms,
      }),
    ]);
    expect(conflicts.length).toBeGreaterThan(0);
  });
});
