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

describe("content library workflow", () => {
  it("filters, searches, sorts, and paginates library content", () => {
    const sidebarFiltered = filterBySidebar(CONTENT_LIBRARY_ITEMS, "articles");
    const toolbarFiltered = filterByToolbar(sidebarFiltered, {
      type: "all",
      status: "all",
      platform: "all",
      dateRange: "all",
      sort: "title-asc",
    });
    const searched = searchContent(toolbarFiltered, "azure");
    const sorted = sortContent(searched, "title-asc");
    const page = paginateItems(sorted, 1, 5);

    expect(sidebarFiltered.every((item) => item.type === "article")).toBe(true);
    expect(sorted.length).toBeGreaterThan(0);
    expect(page.length).toBeLessThanOrEqual(5);
    expect(countBySidebarFilter(CONTENT_LIBRARY_ITEMS, "favorites")).toBeGreaterThan(0);
  });

  it("returns an empty page when search has no matches", () => {
    const filtered = searchContent(CONTENT_LIBRARY_ITEMS, "zzzz-no-match-zzzz");
    expect(filtered).toHaveLength(0);
    expect(paginateItems(filtered, 1, 10)).toHaveLength(0);
  });
});
