import type { ScheduledPost } from "@/lib/domain/scheduler";

import { createFactory } from "./create-factory";

export const scheduledPostFactory = createFactory<ScheduledPost>((sequence) => ({
  id: `sch-${sequence}`,
  title: `Scheduled Post ${sequence}`,
  platforms: ["linkedin"],
  scheduledAt: "2026-08-15T14:00:00.000Z",
  timezone: "America/New_York",
  status: "scheduled",
  priority: "normal",
  thumbnailHue: 200,
  aiVersion: "v1",
  approvalStatus: "approved",
  queueOrder: sequence,
  hasContent: true,
}));
