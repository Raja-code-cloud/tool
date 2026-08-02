import { describe, expect, it } from "vitest";

import {
  applyShorten,
  applyToneTransform,
  computeEngagementScore,
  computeReadabilityScore,
  computeSeoScore,
  countWords,
  getPlatformLimit,
  limitProgress,
  limitStatus,
  splitThreadTweets,
} from "@/lib/utils/ai-studio";

describe("ai studio utilities", () => {
  const sample =
    "Production-ready Azure landing zones help teams ship faster. What patterns are you using today?";

  it("counts words and characters", () => {
    expect(countWords("one two three")).toBe(3);
    expect(countWords("   ")).toBe(0);
  });

  it("evaluates platform limits and status thresholds", () => {
    const limit = getPlatformLimit("linkedin");
    expect(limit).toBeGreaterThan(0);
    expect(limitProgress(limit - 10, limit)).toBeGreaterThan(90);
    expect(limitStatus(limit + 1, limit, limit - 100)).toBe("danger");
    expect(limitStatus(limit - 50, limit, limit - 100)).toBe("warning");
    expect(limitStatus(100, limit, limit - 100)).toBe("ok");
  });

  it("scores content quality heuristics", () => {
    expect(computeSeoScore(sample, ["azure", "cloud", "devops"])).toBeGreaterThan(70);
    expect(computeReadabilityScore(sample)).toBeGreaterThan(50);
    expect(computeEngagementScore(sample, true)).toBeGreaterThan(60);
  });

  it("transforms tone and shortens long content", () => {
    expect(applyToneTransform(sample, "technical")).toContain("[Technical depth]");
    expect(applyShorten(`${sample} ${sample}`, 0.5).endsWith("…")).toBe(true);
  });

  it("splits thread content into tweet-sized chunks", () => {
    expect(splitThreadTweets("First tweet\n\nSecond tweet")).toEqual([
      "First tweet",
      "Second tweet",
    ]);
  });
});
