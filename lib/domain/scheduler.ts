import type { PlatformId } from "@/lib/domain/platform";

export type ScheduleStatus =
  | "draft"
  | "scheduled"
  | "ready"
  | "queued"
  | "publishing"
  | "published"
  | "failed"
  | "cancelled"
  | "expired";
export type SchedulePriority = "low" | "normal" | "high";
export type CalendarView = "month" | "week" | "day" | "agenda";
export type QueueSection =
  "upcoming" | "drafts" | "scheduled" | "publishing" | "published" | "failed" | "cancelled";

export type ScheduledPost = {
  readonly id: string;
  readonly version: number;
  readonly publicationTargetId: string;
  readonly publicationId?: string;
  readonly title: string;
  readonly platforms: readonly PlatformId[];
  readonly scheduledAt: string;
  readonly timezone: string;
  readonly status: ScheduleStatus;
  readonly priority: SchedulePriority;
  readonly thumbnailHue: number;
  readonly aiVersion: string;
  readonly approvalStatus: "approved" | "pending" | "rejected";
  readonly queueOrder: number;
  readonly hasContent: boolean;
};

export type SchedulerNotification = {
  readonly id: string;
  readonly message: string;
  readonly variant: "success" | "warning" | "info";
  readonly timestamp: string;
};
