"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Plus } from "lucide-react";

import { Card } from "@/components/cards";
import { Skeleton } from "@/components/feedback";
import type { CalendarView } from "@/lib/domain/scheduler";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";
import { formatMonthYear } from "@/lib/utils/scheduler";

import { CalendarAgendaView } from "./calendar-agenda-view";
import type { CalendarData, CalendarDragActions, CalendarSelection } from "./calendar-contracts";
import { CalendarDayView } from "./calendar-day-view";
import { CalendarMonthView } from "./calendar-month-view";
import { CalendarWeekView } from "./calendar-week-view";

export type CalendarWorkspaceProps = {
  view: CalendarView;
  data: CalendarData;
  selection: CalendarSelection;
  dragActions: CalendarDragActions;
  isLoading: boolean;
  onQuickAdd: () => void;
};

export function CalendarWorkspace(props: CalendarWorkspaceProps): React.JSX.Element {
  if (props.isLoading) {
    return (
      <Card className="min-h-[480px] p-4">
        <Skeleton className="mb-4 h-8 w-48" />
        <Skeleton className="h-96 w-full" />
      </Card>
    );
  }
  const interactiveProps = {
    data: props.data,
    selection: props.selection,
    dragActions: props.dragActions,
  };
  return (
    <Card className="relative min-h-[480px] overflow-hidden p-0">
      <div className="border-b px-4 py-3">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-heading-3">{formatMonthYear(props.data.currentDate)}</h2>
          <button
            type="button"
            onClick={props.onQuickAdd}
            className="bg-primary text-primary-foreground inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-xs font-semibold hover:brightness-110"
          >
            <Plus className="size-4" aria-hidden="true" /> Quick add
          </button>
        </div>
      </div>
      <AnimatePresence mode="wait">
        <motion.div
          key={props.view + props.data.currentDate.toISOString()}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: MOTION_DURATION.page, ease: MOTION_EASING.enter }}
          className="p-4"
        >
          {props.view === "month" && <CalendarMonthView {...interactiveProps} />}
          {props.view === "week" && <CalendarWeekView {...interactiveProps} />}
          {props.view === "day" && <CalendarDayView {...interactiveProps} />}
          {props.view === "agenda" && <CalendarAgendaView data={props.data} />}
        </motion.div>
      </AnimatePresence>
    </Card>
  );
}
