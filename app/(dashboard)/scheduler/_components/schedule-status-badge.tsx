"use client";

import {
  Ban,
  CalendarClock,
  CheckCircle2,
  Clock,
  FileEdit,
  Loader2,
  Radio,
  XCircle,
} from "lucide-react";

import { StatusBadge } from "@/components/feedback";
import type { ScheduleStatus } from "@/lib/domain/scheduler";

const CONFIG: Record<
  ScheduleStatus,
  {
    variant: "neutral" | "info" | "success" | "warning" | "danger";
    icon: typeof Clock;
    label: string;
  }
> = {
  draft: { variant: "neutral", icon: FileEdit, label: "Draft" },
  scheduled: { variant: "info", icon: CalendarClock, label: "Scheduled" },
  ready: { variant: "info", icon: CheckCircle2, label: "Ready" },
  publishing: { variant: "warning", icon: Loader2, label: "Publishing" },
  published: { variant: "success", icon: CheckCircle2, label: "Published" },
  failed: { variant: "danger", icon: XCircle, label: "Failed" },
  cancelled: { variant: "neutral", icon: Ban, label: "Cancelled" },
};

export function ScheduleStatusBadge({ status }: { status: ScheduleStatus }): React.JSX.Element {
  const config = CONFIG[status];
  const Icon = config.icon;
  return (
    <StatusBadge variant={config.variant}>
      <Icon
        className={`size-3 ${status === "publishing" ? "animate-spin" : ""}`}
        aria-hidden="true"
      />
      {config.label}
    </StatusBadge>
  );
}

export function PriorityIndicator({
  priority,
}: {
  priority: "low" | "normal" | "high";
}): React.JSX.Element {
  const colors = { low: "text-muted-foreground", normal: "text-info", high: "text-warning" };
  return (
    <span
      className={`inline-flex items-center gap-1 text-xs font-semibold ${colors[priority]}`}
      title={`${priority} priority`}
    >
      <Radio className="size-3" aria-hidden="true" />
      <span className="capitalize">{priority}</span>
    </span>
  );
}
