import { postsForDay } from "@/lib/utils/scheduler";

import type { InteractiveCalendarViewProps } from "./calendar-contracts";
import { CalendarEventChip } from "./calendar-event-chip";

export function CalendarDayView({
  data,
  selection,
  dragActions,
}: InteractiveCalendarViewProps): React.JSX.Element {
  const dayPosts = postsForDay(data.posts, data.currentDate).sort(
    (a, b) => new Date(a.scheduledAt).getTime() - new Date(b.scheduledAt).getTime(),
  );
  const hours = Array.from({ length: 14 }, (_, index) => index + 6);
  return (
    <div className="grid gap-1">
      {hours.map((hour) => {
        const hourPosts = dayPosts.filter((post) => new Date(post.scheduledAt).getHours() === hour);
        return (
          <div key={hour} className="grid grid-cols-[4rem_1fr] gap-2 border-b py-2">
            <time className="text-muted-foreground text-xs tabular-nums">{hour}:00</time>
            <div
              className="min-h-10 rounded-lg border border-dashed p-1"
              onDragOver={(event) => event.preventDefault()}
              onDrop={() => {
                if (dragActions.draggedId) {
                  const target = new Date(data.currentDate);
                  target.setHours(hour, 0, 0, 0);
                  dragActions.onReschedule(dragActions.draggedId, target);
                  dragActions.onDragEnd();
                }
              }}
            >
              {hourPosts.length === 0 ? (
                <span className="text-muted-foreground text-xs">—</span>
              ) : (
                hourPosts.map((post) => (
                  <CalendarEventChip
                    key={post.id}
                    post={post}
                    isSelected={selection.selectedId === post.id}
                    timezone={data.timezone}
                    onSelect={() => selection.onSelect(post.id)}
                    onDragStart={() => dragActions.onDragStart(post.id)}
                    onDragEnd={dragActions.onDragEnd}
                  />
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
