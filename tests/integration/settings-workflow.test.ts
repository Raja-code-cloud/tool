import { describe, expect, it } from "vitest";

import { mockSettingsRepository } from "@/lib/adapters/mock-repositories";
import { INPUT_LIMITS, isWithinLimit } from "@/lib/security/input-limits";
import { createSettingsService } from "@/lib/services/workspace-services";

describe("settings workflow", () => {
  const service = createSettingsService(mockSettingsRepository);

  it("loads profile, notification, and provider defaults", () => {
    expect(service.getProfileDefaults().fullName).toBeTruthy();
    expect(service.listNotificationPreferences().length).toBeGreaterThan(0);
    expect(service.listAiProviders().length).toBeGreaterThan(0);
    expect(service.getPublishingDefaults().defaultTimezone).toBeTruthy();
  });

  it("validates dangerous profile input against security limits", () => {
    const projectName = "A".repeat(INPUT_LIMITS.projectName + 1);
    expect(isWithinLimit(projectName, "projectName")).toBe(false);
    expect(service.listActiveSessions().every((session) => session.id.length > 0)).toBe(true);
  });
});
