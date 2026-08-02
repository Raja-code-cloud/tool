import type { ScheduledPost } from "@/lib/domain/scheduler";

export type CalendarData = {
  currentDate: Date;
  posts: readonly ScheduledPost[];
  timezone: string;
};

export type CalendarSelection = {
  selectedId: string | null;
  onSelect: (id: string) => void;
};

export type CalendarDragActions = {
  draggedId: string | null;
  onReschedule: (id: string, day: Date) => void;
  onDragStart: (id: string) => void;
  onDragEnd: () => void;
};

export type InteractiveCalendarViewProps = {
  data: CalendarData;
  selection: CalendarSelection;
  dragActions: CalendarDragActions;
};
