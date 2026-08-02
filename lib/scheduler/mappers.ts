import type {
  PublicationStatusDto,
  ScheduleCalendarDto,
  ScheduleDto,
  ScheduleStateDto,
} from "@/lib/api/scheduler-types";
import type { PlatformId } from "@/lib/domain/platform";
import type { ScheduledPost, ScheduleStatus } from "@/lib/domain/scheduler";

const PLATFORM_CODES: Readonly<Record<string, PlatformId>> = {
  linkedin: "linkedin",
  facebook: "facebook",
  instagram: "instagram",
  x: "x",
  twitter: "x",
  medium: "medium",
  youtube: "youtube",
};

function hashHue(value: string): number {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 31 + value.charCodeAt(index)) % 360;
  }
  return hash;
}

function mapPlatformCode(code: string): PlatformId {
  const normalized = code.toLowerCase();
  return PLATFORM_CODES[normalized] ?? "linkedin";
}

function mapApprovalState(
  value: string,
): "approved" | "pending" | "rejected" {
  if (value === "approved") return "approved";
  if (value === "rejected") return "rejected";
  return "pending";
}

export function mapScheduleStateToStatus(
  scheduleState: ScheduleStateDto,
  publicationStatus?: PublicationStatusDto,
): ScheduleStatus {
  if (scheduleState === "cancelled") return "cancelled";
  if (scheduleState === "failed") return "failed";
  if (scheduleState === "completed") return "published";
  if (scheduleState === "dispatched") return "publishing";

  if (publicationStatus === "draft") return "draft";
  if (publicationStatus === "ready") return "ready";
  if (publicationStatus === "in_progress") return "queued";
  if (publicationStatus === "completed") return "published";
  if (publicationStatus === "partially_failed") return "failed";
  if (publicationStatus === "cancelled") return "cancelled";

  if (scheduleState === "draft") return "draft";
  if (scheduleState === "paused") return "scheduled";
  return "scheduled";
}

export function mapScheduleCalendarDto(dto: ScheduleCalendarDto): ScheduledPost {
  return {
    id: dto.id,
    version: dto.version,
    publicationTargetId: dto.publicationTargetId,
    publicationId: dto.publicationId,
    title: dto.publicationTitle,
    platforms: [mapPlatformCode(dto.platformCode)],
    scheduledAt: dto.scheduledFor,
    timezone: dto.timeZone,
    status: mapScheduleStateToStatus(dto.state, dto.publicationStatus),
    priority: dto.priority,
    thumbnailHue: hashHue(dto.publicationId),
    aiVersion: "v1.0",
    approvalStatus: mapApprovalState(dto.approvalState),
    queueOrder: dto.queueOrder,
    hasContent: true,
  };
}

export function mapScheduleDto(dto: ScheduleDto, fallback?: Partial<ScheduledPost>): ScheduledPost {
  return {
    id: dto.id,
    version: dto.version,
    publicationTargetId: dto.publicationTargetId,
    publicationId: fallback?.publicationId,
    title: fallback?.title ?? `Schedule ${dto.id.slice(0, 8)}`,
    platforms: fallback?.platforms ?? ["linkedin"],
    scheduledAt: dto.scheduledFor,
    timezone: dto.timeZone,
    status: mapScheduleStateToStatus(dto.state),
    priority: dto.priority,
    thumbnailHue: fallback?.thumbnailHue ?? hashHue(dto.id),
    aiVersion: fallback?.aiVersion ?? "v1.0",
    approvalStatus: fallback?.approvalStatus ?? "pending",
    queueOrder: fallback?.queueOrder ?? 0,
    hasContent: fallback?.hasContent ?? true,
  };
}

export function toRequestedLocalAt(date: string, time: string): string {
  return `${date}T${time.length === 5 ? `${time}:00` : time}`;
}

export function toUtcRangeStart(date: Date): string {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate()).toISOString();
}

export function toUtcRangeEnd(date: Date): string {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999).toISOString();
}
