import type { ScheduledPost } from "@/lib/domain/scheduler";
import { cn } from "@/lib/utils/cn";
import { formatDate } from "@/lib/utils/formatting";
import { getWeekDays, isSameDay, isToday } from "@/lib/utils/scheduler";

import type { InteractiveCalendarViewProps } from "./calendar-contracts";
import { CalendarEventChip } from "./calendar-event-chip";

type WeekRowProps = InteractiveCalendarViewProps & { hour: number; days: readonly Date[] };

function WeekRow({ hour, days, data, selection, dragActions }: WeekRowProps): React.JSX.Element {
  return (
    <>
      <div className="text-muted-foreground py-2 text-xs tabular-nums">{hour}:00</div>
      {days.map((day) => {
        const slotPosts: readonly ScheduledPost[] = data.posts.filter((post) => {
          const date = new Date(post.scheduledAt);
          return isSameDay(date, day) && date.getHours() === hour;
        });
        return (
          <div
            key={`${day.toISOString()}-${hour}`}
            className="border-border/60 min-h-12 rounded border border-dashed p-0.5"
            onDragOver={(event) => event.preventDefault()}
            onDrop={() => {
              if (dragActions.draggedId) {
                const target = new Date(day);
                target.setHours(hour, 0, 0, 0);
                dragActions.onReschedule(dragActions.draggedId, target);
                dragActions.onDragEnd();
              }
            }}
          >
            {slotPosts.map((post) => (
              <CalendarEventChip
                key={post.id}
                post={post}
                isSelected={selection.selectedId === post.id}
                timezone={data.timezone}
                compact
                onSelect={() => selection.onSelect(post.id)}
                onDragStart={() => dragActions.onDragStart(post.id)}
                onDragEnd={dragActions.onDragEnd}
              />
            ))}
          </div>
        );
      })}
    </>
  );
}

export function CalendarWeekView(props: InteractiveCalendarViewProps): React.JSX.Element {
  const days = getWeekDays(props.data.currentDate);
  const hours = Array.from({ length: 12 }, (_, index) => index + 7);
  return (
    <div className="overflow-x-auto">
      <div className="grid min-w-[640px] grid-cols-8 gap-1">
        <div />
        {days.map((day) => (
          <div
            key={day.toISOString()}
            className={cn(
              "border-b pb-2 text-center text-xs font-semibold",
              isToday(day) && "text-primary",
            )}
          >
            {formatDate(day, { weekday: "short", day: "numeric" })}
          </div>
        ))}
        {hours.map((hour) => (
          <WeekRow key={hour} hour={hour} days={days} {...props} />
        ))}
      </div>
    </div>
  );
}
