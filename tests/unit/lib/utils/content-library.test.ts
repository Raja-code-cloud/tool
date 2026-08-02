import { describe, expect, it } from "vitest";

import { CONTENT_LIBRARY_ITEMS } from "@/constants/content-library";
import {
  countBySidebarFilter,
  filterBySidebar,
  filterByToolbar,
  paginateItems,
  searchContent,
  sortContent,
} from "@/lib/utils/content-library";
import { contentItemFactory } from "@/tests/factories";

describe("content library utilities", () => {
  it("filters sidebar categories and favorites", () => {
    const items = [
      contentItemFactory.build({ type: "article", status: "published", isFavorite: true }),
      contentItemFactory.build({ type: "video", isFavorite: false, status: "draft" }),
    ];
    expect(filterBySidebar(items, "articles")).toHaveLength(1);
    expect(filterBySidebar(items, "favorites")).toHaveLength(1);
    expect(filterBySidebar(items, "drafts")).toHaveLength(1);
    expect(countBySidebarFilter(items, "videos")).toBe(1);
  });

  it("applies toolbar filters for type, status, platform, and date range", () => {
    const items = [
      contentItemFactory.build({
        type: "poster",
        status: "published",
        platforms: ["Instagram"],
        updatedAt: new Date().toISOString(),
      }),
      contentItemFactory.build({
        type: "article",
        status: "draft",
        platforms: ["LinkedIn"],
        updatedAt: new Date().toISOString(),
      }),
    ];

    expect(
      filterByToolbar(items, {
        type: "poster",
        status: "all",
        platform: "all",
        dateRange: "all",
        sort: "updated-desc",
      }),
    ).toHaveLength(1);

    expect(
      filterByToolbar(items, {
        type: "all",
        status: "all",
        platform: "LinkedIn",
        dateRange: "30d",
        sort: "updated-desc",
      }),
    ).toHaveLength(1);
  });

  it("searches across title, tags, and platforms", () => {
    const results = searchContent(CONTENT_LIBRARY_ITEMS, "terraform");
    expect(results.length).toBeGreaterThan(0);
    expect(
      results.every(
        (item) =>
          item.title.toLowerCase().includes("terraform") ||
          item.tags.join(" ").includes("terraform"),
      ),
    ).toBe(true);
  });

  it("sorts using every supported sort key", () => {
    const items = [
      contentItemFactory.build({
        id: "b",
        title: "Beta",
        updatedAt: "2026-01-02T00:00:00.000Z",
        createdAt: "2026-01-02T00:00:00.000Z",
        author: "Zoe",
      }),
      contentItemFactory.build({
        id: "a",
        title: "Alpha",
        updatedAt: "2026-01-01T00:00:00.000Z",
        createdAt: "2026-01-01T00:00:00.000Z",
        author: "Amy",
        type: "video",
        status: "published",
      }),
    ];

    expect(sortContent(items, "title-asc")[0]?.title).toBe("Alpha");
    expect(sortContent(items, "title-desc")[0]?.title).toBe("Beta");
    expect(sortContent(items, "updated-asc")[0]?.id).toBe("a");
    expect(sortContent(items, "created-desc")[0]?.id).toBe("b");
    expect(sortContent(items, "author-asc")[0]?.author).toBe("Amy");
    expect(sortContent(items, "type-desc")[0]?.type).toBe("video");
    expect(sortContent(items, "status-desc")[0]?.status).toBe("published");
  });

  it("sorts by title and paginates results", () => {
    const sorted = sortContent(CONTENT_LIBRARY_ITEMS, "title-asc");
    expect(sorted[0]?.title.localeCompare(sorted[1]?.title ?? "")).toBeLessThanOrEqual(0);

    const page = paginateItems(sorted, 2, 5);
    expect(page).toHaveLength(5);
    expect(page[0]?.id).toBe(sorted[5]?.id);
  });
});
