import { describe, expect, it } from "vitest";

import {
  applyToneTransform,
  computeEngagementScore,
  getPlatformLimit,
  limitStatus,
  splitThreadTweets,
} from "@/lib/utils/ai-studio";

describe("ai studio workflow", () => {
  const draft =
    "Production-ready Azure landing zones help teams ship faster.\n\nWhat patterns are you using today?";

  it("evaluates platform limits and engagement heuristics during generation", () => {
    const limit = getPlatformLimit("linkedin");
    expect(limitStatus(draft.length, limit, limit - 200)).toBe("ok");
    expect(computeEngagementScore(draft, true)).toBeGreaterThan(60);
  });

  it("applies tone transforms and thread splitting for preview output", () => {
    const technical = applyToneTransform(draft, "technical");
    expect(technical).toContain("[Technical depth]");
    expect(splitThreadTweets(technical).length).toBeGreaterThan(0);
  });
});
