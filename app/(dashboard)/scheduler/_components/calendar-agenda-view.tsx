import { AgendaList } from "@/components/calendar";
import type { ScheduledPost } from "@/lib/domain/scheduler";
import { formatDate } from "@/lib/utils/formatting";
import { formatScheduleTime } from "@/lib/utils/scheduler";

import type { CalendarData } from "./calendar-contracts";
import { ScheduleStatusBadge } from "./schedule-status-badge";
import { SchedulerEmptyState } from "./scheduler-empty-states";

export function CalendarAgendaView({ data }: { data: CalendarData }): React.JSX.Element {
  const sorted = [...data.posts].sort(
    (a, b) => new Date(a.scheduledAt).getTime() - new Date(b.scheduledAt).getTime(),
  );
  const upcoming = sorted.filter((post) => new Date(post.scheduledAt) >= data.currentDate);
  if (upcoming.length === 0) return <SchedulerEmptyState variant="no-scheduled" />;
  const grouped = upcoming.reduce<Record<string, ScheduledPost[]>>((acc, post) => {
    const key = new Date(post.scheduledAt).toDateString();
    acc[key] = acc[key] ?? [];
    acc[key].push(post);
    return acc;
  }, {});
  return (
    <div className="grid gap-6">
      {Object.entries(grouped).map(([dateKey, items]) => (
        <AgendaList
          key={dateKey}
          dateLabel={formatDate(new Date(dateKey), {
            weekday: "long",
            month: "long",
            day: "numeric",
          })}
          items={items.map((post) => ({
            id: post.id,
            time: formatScheduleTime(post.scheduledAt, data.timezone),
            title: post.title,
            meta: post.platforms.join(", "),
            status: <ScheduleStatusBadge status={post.status} />,
          }))}
        />
      ))}
    </div>
  );
}
