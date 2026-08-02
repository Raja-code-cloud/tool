import { describe, expect, it } from "vitest";

import { mockSettingsRepository } from "@/lib/adapters/mock-repositories";
import { INPUT_LIMITS, isWithinLimit } from "@/lib/security/input-limits";
import { createSettingsService } from "@/lib/services/workspace-services";

describe("settings workflow", () => {
  const service = createSettingsService(mockSettingsRepository);

  it("loads profile, notification, and provider defaults", async () => {
    const profile = await service.getProfile();
    expect(profile.fullName).toBeTruthy();
    expect((await service.listNotificationPreferences()).length).toBeGreaterThan(0);
    expect((await service.listAiProviders()).length).toBeGreaterThan(0);
    expect((await service.getPublishingDefaults()).defaultTimezone).toBeTruthy();
  });

  it("validates dangerous profile input against security limits", async () => {
    const projectName = "A".repeat(INPUT_LIMITS.projectName + 1);
    expect(isWithinLimit(projectName, "projectName")).toBe(false);
    expect((await service.listActiveSessions()).every((session) => session.id.length > 0)).toBe(
      true,
    );
  });
});
