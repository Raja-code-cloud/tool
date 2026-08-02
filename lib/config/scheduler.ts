import { PLATFORM_VISUALS } from "@/lib/config/platforms";
import type { PlatformVisual } from "@/lib/domain/platform";
import type { QueueSection, ScheduleStatus } from "@/lib/domain/scheduler";

export const SCHEDULER_PLATFORMS: readonly PlatformVisual[] = PLATFORM_VISUALS;
export const SCHEDULER_TIMEZONES = [
  { value: "America/New_York", label: "Eastern (ET)" },
  { value: "America/Chicago", label: "Central (CT)" },
  { value: "America/Denver", label: "Mountain (MT)" },
  { value: "America/Los_Angeles", label: "Pacific (PT)" },
  { value: "Europe/London", label: "London (GMT)" },
  { value: "Asia/Kolkata", label: "India (IST)" },
  { value: "UTC", label: "UTC" },
] as const;
export const SCHEDULE_STATUSES: readonly { value: ScheduleStatus | "all"; label: string }[] = [
  { value: "all", label: "All statuses" },
  { value: "draft", label: "Draft" },
  { value: "scheduled", label: "Scheduled" },
  { value: "ready", label: "Ready" },
  { value: "publishing", label: "Publishing" },
  { value: "published", label: "Published" },
  { value: "failed", label: "Failed" },
  { value: "cancelled", label: "Cancelled" },
];
export const QUEUE_SECTIONS: readonly {
  id: QueueSection;
  label: string;
  statuses: readonly ScheduleStatus[];
}[] = [
  { id: "upcoming", label: "Upcoming", statuses: ["scheduled", "ready"] },
  { id: "drafts", label: "Drafts", statuses: ["draft"] },
  { id: "scheduled", label: "Scheduled", statuses: ["scheduled"] },
  { id: "publishing", label: "Publishing", statuses: ["publishing"] },
  { id: "published", label: "Published", statuses: ["published"] },
  { id: "failed", label: "Failed", statuses: ["failed"] },
  { id: "cancelled", label: "Cancelled", statuses: ["cancelled"] },
];
