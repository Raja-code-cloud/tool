"use client";

import { CalendarClock, Copy, Pencil, Play, Trash2, XCircle } from "lucide-react";

import {
  DestructiveButton,
  OutlineButton,
  PrimaryButton,
  SecondaryButton,
} from "@/components/buttons";
import { Card, CardHeader } from "@/components/cards";
import { KeyValueList } from "@/components/common";
import { Skeleton } from "@/components/feedback";
import { PlatformChip } from "@/components/platform";
import { Badge } from "@/components/ui";
import { SCHEDULER_TIMEZONES } from "@/lib/config/scheduler";
import type { ScheduledPost } from "@/lib/domain/scheduler";
import { thumbnailGradient } from "@/lib/utils/content-display";
import { formatScheduleDate, formatScheduleTime } from "@/lib/utils/scheduler";

import { PriorityIndicator, ScheduleStatusBadge } from "./schedule-status-badge";
import { SchedulerEmptyState } from "./scheduler-empty-states";

export type DetailsPanelProps = {
  post: ScheduledPost | null;
  isLoading: boolean;
  timezone: string;
  hasConflict: boolean;
  onEdit: () => void;
  onDuplicate: () => void;
  onCancel: () => void;
  onDelete: () => void;
  onPublishNow: () => void;
  onReschedule: () => void;
};

export function DetailsPanel({
  post,
  isLoading,
  timezone,
  hasConflict,
  onEdit,
  onDuplicate,
  onCancel,
  onDelete,
  onPublishNow,
  onReschedule,
}: DetailsPanelProps): React.JSX.Element {
  if (isLoading) {
    return (
      <Card className="p-4">
        <Skeleton className="h-6 w-40" />
        <Skeleton className="mt-4 aspect-video w-full" />
        <Skeleton className="mt-4 h-24 w-full" />
      </Card>
    );
  }

  if (!post) {
    return (
      <Card className="p-4">
        <SchedulerEmptyState variant="no-selection" />
      </Card>
    );
  }

  const tzLabel =
    SCHEDULER_TIMEZONES.find((tz) => tz.value === post.timezone)?.label ?? post.timezone;

  return (
    <div className="grid gap-4">
      <Card className="overflow-hidden p-0">
        <div className="border-b p-4">
          <CardHeader
            title="Details & insights"
            description="Selected schedule event."
            headingLevel={2}
            className="mb-0"
          />
        </div>
        <div className="p-4">
          <div
            className="aspect-video w-full rounded-lg"
            style={{ background: thumbnailGradient(post.thumbnailHue) }}
            role="img"
            aria-label={`Poster for ${post.title}`}
          />
          <h3 className="text-heading-3 mt-4">{post.title}</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {post.platforms.map((platform) => (
              <PlatformChip key={platform} platform={platform} />
            ))}
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <ScheduleStatusBadge status={post.status} />
            <PriorityIndicator priority={post.priority} />
            {hasConflict && <Badge variant="danger">Conflict</Badge>}
          </div>

          <KeyValueList
            className="mt-4"
            items={[
              {
                id: "date",
                term: "Schedule date",
                description: formatScheduleDate(post.scheduledAt, timezone),
              },
              {
                id: "time",
                term: "Time",
                description: formatScheduleTime(post.scheduledAt, timezone),
              },
              { id: "tz", term: "Timezone", description: tzLabel },
              { id: "ai", term: "AI version", description: post.aiVersion },
              {
                id: "approval",
                term: "Approval",
                description:
                  post.approvalStatus.charAt(0).toUpperCase() + post.approvalStatus.slice(1),
              },
            ]}
          />
        </div>

        <div className="grid gap-2 border-t p-4 sm:grid-cols-2">
          <SecondaryButton type="button" onClick={onEdit}>
            <Pencil className="size-4" aria-hidden="true" /> Edit schedule
          </SecondaryButton>
          <SecondaryButton type="button" onClick={onDuplicate}>
            <Copy className="size-4" aria-hidden="true" /> Duplicate
          </SecondaryButton>
          <OutlineButton type="button" onClick={onReschedule}>
            <CalendarClock className="size-4" aria-hidden="true" /> Reschedule
          </OutlineButton>
          <PrimaryButton
            type="button"
            onClick={onPublishNow}
            disabled={post.status === "published" || post.status === "cancelled"}
          >
            <Play className="size-4" aria-hidden="true" /> Publish now
          </PrimaryButton>
          <SecondaryButton type="button" onClick={onCancel} disabled={post.status === "cancelled"}>
            <XCircle className="size-4" aria-hidden="true" /> Cancel
          </SecondaryButton>
          <DestructiveButton type="button" onClick={onDelete}>
            <Trash2 className="size-4" aria-hidden="true" /> Delete
          </DestructiveButton>
        </div>
      </Card>
    </div>
  );
}
