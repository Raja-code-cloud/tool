import { describe, expect, it } from "vitest";

import {
  INITIAL_WIZARD_STATE,
  validateStep,
  wizardProgressPercent,
} from "@/app/(dashboard)/upload/_components/wizard-types";

describe("upload wizard workflow", () => {
  it("blocks progression until each step is valid", () => {
    expect(validateStep(1, INITIAL_WIZARD_STATE).valid).toBe(false);

    const stepOne = {
      ...INITIAL_WIZARD_STATE,
      projectName: "Azure Launch",
      category: "cloud",
    };
    expect(validateStep(1, stepOne).valid).toBe(true);
    expect(validateStep(2, stepOne).valid).toBe(false);

    const stepTwo = {
      ...stepOne,
      poster: {
        name: "poster.png",
        size: 1024,
        type: "image/png",
        previewUrl: "blob:poster",
        progress: 100,
        status: "complete" as const,
      },
    };
    expect(validateStep(2, stepTwo).valid).toBe(true);
    expect(validateStep(3, { ...stepTwo, articleContent: "A".repeat(60) }).valid).toBe(true);
  });

  it("tracks wizard progress across eight steps", () => {
    expect(wizardProgressPercent(1)).toBe(0);
    expect(wizardProgressPercent(4)).toBe(43);
    expect(wizardProgressPercent(8)).toBe(100);
  });
});
