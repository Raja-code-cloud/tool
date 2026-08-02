import type { CalendarView, QueueSection } from "@/lib/domain/scheduler";

export type MobilePanel = "queue" | "calendar" | "details";

export type LoadingArea = "calendar" | "queue" | "details" | null;

export type QuickScheduleForm = {
  title: string;
  platform: string;
  date: string;
  time: string;
  timezone: string;
  priority: "low" | "normal" | "high";
  publicationTargetId?: string;
};

export const DEFAULT_QUICK_SCHEDULE: QuickScheduleForm = {
  title: "",
  platform: "linkedin",
  date: "2026-08-02",
  time: "09:00",
  timezone: "America/New_York",
  priority: "normal",
};

export type SchedulerUiState = {
  view: CalendarView;
  currentDate: Date;
  selectedId: string | null;
  activeQueueSection: QueueSection;
  timezone: string;
  mobilePanel: MobilePanel;
  quickScheduleOpen: boolean;
  loadingArea: LoadingArea;
};

export const REFERENCE_DATE = new Date(2026, 7, 2);
