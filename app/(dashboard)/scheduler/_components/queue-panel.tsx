"use client";

import { motion } from "framer-motion";
import { CalendarPlus, ChevronDown, ChevronUp, Copy, MoreHorizontal } from "lucide-react";

import { IconButton, OutlineButton } from "@/components/buttons";
import { Card, CardHeader } from "@/components/cards";
import { Skeleton } from "@/components/feedback";
import { PlatformDots } from "@/components/platform";
import { QUEUE_SECTIONS } from "@/lib/config/scheduler";
import type { QueueSection, ScheduledPost } from "@/lib/domain/scheduler";
import { cn } from "@/lib/utils/cn";
import { thumbnailGradient } from "@/lib/utils/content-display";
import { formatScheduleDate, formatScheduleTime } from "@/lib/utils/scheduler";

import { PriorityIndicator, ScheduleStatusBadge } from "./schedule-status-badge";
import { SchedulerEmptyState } from "./scheduler-empty-states";

export type QueuePanelProps = {
  posts: readonly ScheduledPost[];
  activeSection: QueueSection;
  onSectionChange: (section: QueueSection) => void;
  selectedId: string | null;
  onSelect: (id: string) => void;
  onReorder: (fromId: string, toId: string) => void;
  draggedId: string | null;
  onDragStart: (id: string) => void;
  onDragEnd: () => void;
  conflictPostIds: ReadonlySet<string>;
  isLoading: boolean;
  timezone: string;
};

export function QueuePanel({
  posts,
  activeSection,
  onSectionChange,
  selectedId,
  onSelect,
  onReorder,
  draggedId,
  onDragStart,
  onDragEnd,
  conflictPostIds,
  isLoading,
  timezone,
}: QueuePanelProps): React.JSX.Element {
  const section = QUEUE_SECTIONS.find((item) => item.id === activeSection);
  const sectionPosts = posts
    .filter((post) => section?.statuses.includes(post.status))
    .sort((a, b) => a.queueOrder - b.queueOrder);

  return (
    <Card className="flex h-full flex-col overflow-hidden p-0">
      <div className="border-b p-4">
        <CardHeader
          title="Publishing queue"
          description="Upcoming posts and publishing pipeline."
          headingLevel={2}
          className="mb-3"
        />
        <nav aria-label="Queue sections" className="flex flex-wrap gap-1">
          {QUEUE_SECTIONS.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => onSectionChange(item.id)}
              aria-current={activeSection === item.id ? "true" : undefined}
              className={cn(
                "rounded-md px-2 py-1 text-xs font-semibold transition-colors",
                activeSection === item.id
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted",
              )}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {isLoading ? (
          <div className="grid gap-2">
            {Array.from({ length: 4 }, (_, index) => (
              <Skeleton key={index} className="h-20 w-full" />
            ))}
          </div>
        ) : sectionPosts.length === 0 ? (
          <SchedulerEmptyState variant="no-queue" />
        ) : (
          <>
            <p id="queue-reorder-instructions" className="sr-only">
              Use the move up and move down buttons to reorder queue items. Drag and drop is also
              available with a pointer.
            </p>
            <ul
              className="grid gap-2"
              aria-label={`${section?.label ?? "Queue"} items`}
              aria-describedby="queue-reorder-instructions"
            >
              {sectionPosts.map((post, index) => (
                <QueueItem
                  key={post.id}
                  post={post}
                  index={index}
                  queueLength={sectionPosts.length}
                  isSelected={selectedId === post.id}
                  hasConflict={conflictPostIds.has(post.id)}
                  timezone={timezone}
                  isDragging={draggedId === post.id}
                  onSelect={() => onSelect(post.id)}
                  onDragStart={() => onDragStart(post.id)}
                  onDragEnd={onDragEnd}
                  onDrop={() => {
                    if (draggedId && draggedId !== post.id) onReorder(draggedId, post.id);
                    onDragEnd();
                  }}
                  onMoveUp={() => {
                    if (index > 0) onReorder(post.id, sectionPosts[index - 1]!.id);
                  }}
                  onMoveDown={() => {
                    if (index < sectionPosts.length - 1)
                      onReorder(post.id, sectionPosts[index + 1]!.id);
                  }}
                />
              ))}
            </ul>
          </>
        )}
      </div>
    </Card>
  );
}

type QueueItemProps = {
  post: ScheduledPost;
  index: number;
  queueLength: number;
  isSelected: boolean;
  hasConflict: boolean;
  timezone: string;
  isDragging: boolean;
  onSelect: () => void;
  onDragStart: () => void;
  onDragEnd: () => void;
  onDrop: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
};

function QueueItem({
  post,
  index,
  queueLength,
  isSelected,
  hasConflict,
  timezone,
  isDragging,
  onSelect,
  onDragStart,
  onDragEnd,
  onDrop,
  onMoveUp,
  onMoveDown,
}: QueueItemProps): React.JSX.Element {
  return (
    <motion.li
      layout
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      onDragOver={(event) => event.preventDefault()}
      onDrop={onDrop}
      className={cn(
        "bg-card cursor-grab rounded-lg border p-2.5 transition-shadow active:cursor-grabbing",
        isSelected && "border-primary ring-primary/30 ring-1",
        isDragging && "opacity-60 shadow-lg",
        hasConflict && "border-destructive/50",
      )}
    >
      <button type="button" className="flex w-full gap-2.5 text-left" onClick={onSelect}>
        <div
          className="size-12 shrink-0 rounded-md"
          style={{ background: thumbnailGradient(post.thumbnailHue) }}
          role="img"
          aria-label={`Thumbnail for ${post.title}`}
        />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold">{post.title}</p>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <PlatformDots platforms={post.platforms} />
            <PriorityIndicator priority={post.priority} />
          </div>
          <p className="text-muted-foreground mt-1 text-xs">
            {formatScheduleDate(post.scheduledAt, timezone)} ·{" "}
            {formatScheduleTime(post.scheduledAt, timezone)}
          </p>
          <div className="mt-1.5">
            <ScheduleStatusBadge status={post.status} />
          </div>
        </div>
      </button>
      <div className="mt-2 flex justify-end gap-1">
        <IconButton
          label={`Move ${post.title} up in queue`}
          icon={<ChevronUp className="size-4" aria-hidden="true" />}
          onClick={onMoveUp}
          disabled={index === 0}
        />
        <IconButton
          label={`Move ${post.title} down in queue`}
          icon={<ChevronDown className="size-4" aria-hidden="true" />}
          onClick={onMoveDown}
          disabled={index >= queueLength - 1}
        />
        <IconButton
          label="Duplicate"
          icon={<Copy className="size-4" aria-hidden="true" />}
          onClick={onSelect}
        />
        <IconButton
          label="More actions"
          icon={<MoreHorizontal className="size-4" aria-hidden="true" />}
          onClick={onSelect}
        />
      </div>
    </motion.li>
  );
}

export function QuickAddQueueButton({ onClick }: { onClick: () => void }): React.JSX.Element {
  return (
    <OutlineButton type="button" size="compact" onClick={onClick} className="w-full">
      <CalendarPlus className="size-4" aria-hidden="true" /> Quick add
    </OutlineButton>
  );
}
