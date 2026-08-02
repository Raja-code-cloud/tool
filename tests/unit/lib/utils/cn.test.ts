import { describe, expect, it } from "vitest";

import { cn } from "@/lib/utils/cn";

describe("cn utility", () => {
  it("merges class names and resolves Tailwind conflicts", () => {
    expect(cn("px-2", "px-4", false && "hidden", "text-sm")).toBe("px-4 text-sm");
  });

  it("handles arrays, objects, and undefined inputs", () => {
    expect(cn(["rounded-md", "border"], { "bg-card": true, hidden: false })).toBe(
      "rounded-md border bg-card",
    );
    expect(cn(undefined, null, "p-4")).toBe("p-4");
  });

  it("preserves non-conflicting utility classes", () => {
    expect(cn("text-sm font-medium", "text-foreground")).toBe(
      "text-sm font-medium text-foreground",
    );
  });
});
