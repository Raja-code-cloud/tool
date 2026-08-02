import { describe, expect, it } from "vitest";

import {
  contentTypeAbbreviation,
  formatContentStatus,
  formatContentType,
  formatPublishingStatus,
  thumbnailGradient,
} from "@/lib/utils/content-display";

describe("content display utilities", () => {
  it("formats content labels", () => {
    expect(formatContentType("article")).toBe("Article");
    expect(formatContentStatus("draft")).toBe("Draft");
    expect(formatPublishingStatus("live")).toBe("Live");
    expect(contentTypeAbbreviation("video")).toBe("VI");
  });

  it("builds thumbnail gradients from hue values", () => {
    expect(thumbnailGradient(210)).toContain("hsl(210");
    expect(thumbnailGradient(350)).toContain("linear-gradient");
  });
});
