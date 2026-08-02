import { cn } from "@/lib/utils/cn";
import {
  getMonthGridDays,
  isSameMonth,
  isToday,
  isWeekend,
  postsForDay,
} from "@/lib/utils/scheduler";

import type { InteractiveCalendarViewProps } from "./calendar-contracts";
import { CalendarEventChip } from "./calendar-event-chip";

export function CalendarMonthView({
  data,
  selection,
  dragActions,
}: InteractiveCalendarViewProps): React.JSX.Element {
  const days = getMonthGridDays(data.currentDate);
  const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  return (
    <div>
      <div className="mb-2 grid grid-cols-7 gap-1">
        {weekdays.map((day) => (
          <div key={day} className="text-muted-foreground py-1 text-center text-xs font-semibold">
            {day}
          </div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {days.map((day) => {
          const dayPosts = postsForDay(data.posts, day);
          const inMonth = isSameMonth(day, data.currentDate);
          return (
            <div
              key={day.toISOString()}
              className={cn(
                "min-h-24 rounded-lg border p-1 transition-colors",
                isToday(day) && "border-primary bg-accent/30",
                isWeekend(day) && !isToday(day) && "bg-muted/20",
                !inMonth && "opacity-50",
              )}
              onDragOver={(event) => event.preventDefault()}
              onDrop={() => {
                if (dragActions.draggedId) {
                  dragActions.onReschedule(dragActions.draggedId, day);
                  dragActions.onDragEnd();
                }
              }}
            >
              <p
                className={cn(
                  "mb-1 text-xs font-semibold tabular-nums",
                  isToday(day) && "text-primary",
                )}
              >
                {day.getDate()}
              </p>
              <ul className="grid gap-0.5">
                {dayPosts.slice(0, 3).map((post) => (
                  <CalendarEventChip
                    key={post.id}
                    post={post}
                    isSelected={selection.selectedId === post.id}
                    timezone={data.timezone}
                    onSelect={() => selection.onSelect(post.id)}
                    onDragStart={() => dragActions.onDragStart(post.id)}
                    onDragEnd={dragActions.onDragEnd}
                  />
                ))}
                {dayPosts.length > 3 && (
                  <li className="text-muted-foreground text-[10px]">+{dayPosts.length - 3} more</li>
                )}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}
