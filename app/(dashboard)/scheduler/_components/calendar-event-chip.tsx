"use client";

import { getPlatformVisual } from "@/lib/config/platforms";
import type { ScheduledPost } from "@/lib/domain/scheduler";
import { cn } from "@/lib/utils/cn";
import { thumbnailGradient } from "@/lib/utils/content-display";
import { formatScheduleTime } from "@/lib/utils/scheduler";

export type CalendarEventChipProps = {
  post: ScheduledPost;
  isSelected: boolean;
  timezone: string;
  compact?: boolean;
  onSelect: () => void;
  onDragStart: () => void;
  onDragEnd: () => void;
};

export function CalendarEventChip(props: CalendarEventChipProps): React.JSX.Element {
  const platform = getPlatformVisual(props.post.platforms[0] ?? "linkedin");
  return (
    <li>
      <button
        type="button"
        draggable
        onDragStart={props.onDragStart}
        onDragEnd={props.onDragEnd}
        onClick={props.onSelect}
        title={`${props.post.title} · ${formatScheduleTime(props.post.scheduledAt, props.timezone)}`}
        className={cn(
          "group flex w-full items-center gap-1 rounded border px-1 py-0.5 text-left text-[10px] font-semibold transition-transform hover:scale-[1.02]",
          platform.bgClass,
          platform.borderClass,
          props.isSelected && "ring-primary ring-1",
          props.compact && "truncate",
        )}
      >
        <span
          className="size-3 shrink-0 rounded-sm"
          style={{ background: thumbnailGradient(props.post.thumbnailHue) }}
          aria-hidden="true"
        />
        <span className="truncate">{props.post.title}</span>
      </button>
    </li>
  );
}
