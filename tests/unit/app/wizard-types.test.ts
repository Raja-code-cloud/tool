import { describe, expect, it } from "vitest";

import {
  completedSteps,
  countWords,
  estimateReadingMinutes,
  firstInvalidWizardFieldId,
  INITIAL_WIZARD_STATE,
  validateStep,
  wizardErrorFieldId,
  wizardProgressPercent,
} from "@/app/(dashboard)/upload/_components/wizard-types";

describe("upload wizard validation", () => {
  it("requires project metadata on step 1", () => {
    const result = validateStep(1, INITIAL_WIZARD_STATE);
    expect(result.valid).toBe(false);
    expect(result.errors.projectName).toBeTruthy();
    expect(result.errors.category).toBeTruthy();
  });

  it("accepts valid project metadata", () => {
    const result = validateStep(1, {
      ...INITIAL_WIZARD_STATE,
      projectName: "Azure Launch",
      category: "cloud",
    });
    expect(result.valid).toBe(true);
  });

  it("requires a completed poster on step 2", () => {
    const result = validateStep(2, INITIAL_WIZARD_STATE);
    expect(result.errors.poster).toContain("Upload a poster");
  });

  it("requires article content or file on step 3", () => {
    const pasteInvalid = validateStep(3, {
      ...INITIAL_WIZARD_STATE,
      articleMode: "paste",
      articleContent: "too short",
    });
    expect(pasteInvalid.errors.articleContent).toBeTruthy();

    const pasteValid = validateStep(3, {
      ...INITIAL_WIZARD_STATE,
      articleMode: "paste",
      articleContent: "A".repeat(60),
    });
    expect(pasteValid.valid).toBe(true);
  });

  it("requires platforms and tone on step 6", () => {
    const result = validateStep(6, { ...INITIAL_WIZARD_STATE, platforms: [] });
    expect(result.errors.platforms).toBeTruthy();
  });

  it("tracks completed steps and progress", () => {
    const state = {
      ...INITIAL_WIZARD_STATE,
      projectName: "Azure Launch",
      category: "cloud",
    };
    expect(completedSteps(state, 2)).toEqual([1]);
    expect(wizardProgressPercent(1)).toBe(0);
    expect(wizardProgressPercent(8)).toBe(100);
  });

  it("maps validation errors to focusable field ids", () => {
    expect(wizardErrorFieldId("projectName")).toBe("project-name");
    expect(firstInvalidWizardFieldId({ projectName: "Required" })).toBe("project-name");
  });

  it("estimates reading time from word count", () => {
    expect(countWords("one two three four")).toBe(4);
    expect(estimateReadingMinutes(400)).toBe(2);
  });
});
