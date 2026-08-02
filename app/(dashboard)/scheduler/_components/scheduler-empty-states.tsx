"use client";

import { CalendarX, Inbox, SearchX } from "lucide-react";

import { EmptyState } from "@/components/feedback";

export type SchedulerEmptyVariant =
  "no-scheduled" | "no-search" | "no-platform" | "no-queue" | "no-selection";

const COPY: Record<SchedulerEmptyVariant, { title: string; description: string }> = {
  "no-scheduled": {
    title: "No scheduled posts",
    description: "Create a schedule to see events on the calendar.",
  },
  "no-search": { title: "No search results", description: "Try adjusting your search or filters." },
  "no-platform": {
    title: "No platform selected",
    description: "Select a platform filter to narrow results.",
  },
  "no-queue": { title: "No queue items", description: "This section has no posts right now." },
  "no-selection": {
    title: "No event selected",
    description: "Select a calendar event or queue item to view details.",
  },
};

const ICONS = {
  "no-scheduled": CalendarX,
  "no-search": SearchX,
  "no-platform": Inbox,
  "no-queue": Inbox,
  "no-selection": CalendarX,
} as const;

export function SchedulerEmptyState({
  variant,
}: {
  variant: SchedulerEmptyVariant;
}): React.JSX.Element {
  const copy = COPY[variant];
  const Icon = ICONS[variant];
  return (
    <EmptyState
      title={copy.title}
      description={copy.description}
      icon={<Icon aria-hidden="true" />}
      className="min-h-40 border-solid bg-transparent p-4"
    />
  );
}
