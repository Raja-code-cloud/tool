"use client";

import { Archive, CalendarClock, CheckCircle2, Clock, FileEdit } from "lucide-react";

import { StatusBadge } from "@/components/feedback";
import type { ContentStatus, PublishingStatus } from "@/lib/domain/content";

const STATUS_VARIANT = {
  draft: "neutral",
  scheduled: "info",
  published: "success",
  archived: "warning",
} as const;

const PUBLISHING_VARIANT = {
  not_started: "neutral",
  queued: "info",
  live: "success",
  failed: "danger",
} as const;

const STATUS_ICON = {
  draft: FileEdit,
  scheduled: CalendarClock,
  published: CheckCircle2,
  archived: Archive,
} as const;

export function ContentStatusBadge({ status }: { status: ContentStatus }): React.JSX.Element {
  const Icon = STATUS_ICON[status];
  return (
    <StatusBadge variant={STATUS_VARIANT[status]}>
      <Icon className="size-3" aria-hidden="true" />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </StatusBadge>
  );
}

export function PublishingStatusBadge({ status }: { status: PublishingStatus }): React.JSX.Element {
  return (
    <StatusBadge variant={PUBLISHING_VARIANT[status]}>
      <Clock className="size-3" aria-hidden="true" />
      {status === "not_started" ? "Not started" : status.charAt(0).toUpperCase() + status.slice(1)}
    </StatusBadge>
  );
}
