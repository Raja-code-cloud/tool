"use client";

import type { HTMLAttributes, ReactNode } from "react";
import * as React from "react";
import { CalendarIcon } from "lucide-react";
import { DayPicker, type DateRange, type PropsRange, type PropsSingle } from "react-day-picker";

import { cn } from "@/lib/utils/cn";
import { Button } from "@/components/ui";
import { formatDate } from "@/lib/utils/formatting";

export type CalendarSingleProps = Omit<PropsSingle, "mode"> & { className?: string };
export function CalendarSingle({ className, ...props }: CalendarSingleProps): React.JSX.Element {
  return <DayPicker mode="single" aria-label="Choose a date" className={cn("rounded-lg border bg-card p-3", className)} classNames={calendarClassNames} {...props} />;
}

export type DatePickerProps = { value?: Date; onChange: (date: Date | undefined) => void; label?: string; disabled?: boolean; className?: string };
export function DatePicker({ value, onChange, label = "Choose date", disabled, className }: DatePickerProps): React.JSX.Element {
  const [isOpen, setIsOpen] = React.useState(false);
  return <div className={cn("relative inline-block", className)}><Button type="button" variant="outline" disabled={disabled} aria-expanded={isOpen} aria-haspopup="dialog" onClick={() => setIsOpen((current) => !current)}><CalendarIcon aria-hidden="true" />{value ? formatDate(value) : label}</Button>{isOpen && <div role="dialog" aria-label={label} className="absolute top-full left-0 z-50 mt-2 shadow-popover"><CalendarSingle selected={value} onSelect={(date) => { onChange(date); setIsOpen(false); }} /></div>}</div>;
}

export type CalendarRangeProps = Omit<PropsRange, "mode"> & { className?: string; selected?: DateRange };
export function CalendarRange({ className, ...props }: CalendarRangeProps): React.JSX.Element {
  return <DayPicker mode="range" className={cn("rounded-lg border bg-card p-3", className)} classNames={calendarClassNames} {...props} />;
}

export type AgendaItem = { id: string; time: string; title: string; meta?: ReactNode; status?: ReactNode };
export type AgendaListProps = HTMLAttributes<HTMLUListElement> & { dateLabel: string; items: readonly AgendaItem[]; empty?: ReactNode };
export function AgendaList({ dateLabel, items, empty = "Nothing scheduled.", className, ...props }: AgendaListProps): React.JSX.Element {
  return <section aria-labelledby="agenda-heading"><h3 id="agenda-heading" className="mb-3 font-semibold">{dateLabel}</h3>{items.length === 0 ? <p className="text-sm text-muted-foreground">{empty}</p> : <ul className={cn("grid gap-2", className)} {...props}>{items.map((item) => <li key={item.id} className="grid grid-cols-[auto_1fr_auto] gap-3 rounded-lg border bg-card p-3"><time className="text-xs font-semibold tabular-nums">{item.time}</time><div><p className="text-sm font-semibold">{item.title}</p>{item.meta && <div className="mt-1 text-xs text-muted-foreground">{item.meta}</div>}</div>{item.status}</li>)}</ul>}</section>;
}

const calendarClassNames = {
  months: "flex flex-col gap-4 sm:flex-row",
  month_caption: "relative flex h-10 items-center justify-center font-semibold",
  nav: "absolute inset-x-2 top-3 flex justify-between",
  button_previous: "grid size-9 place-items-center rounded-md hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
  button_next: "grid size-9 place-items-center rounded-md hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
  month_grid: "w-full border-collapse",
  weekdays: "flex",
  weekday: "w-10 text-center text-xs text-muted-foreground",
  week: "mt-1 flex",
  day: "size-10 text-center text-sm",
  day_button: "size-10 rounded-md hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
  selected: "rounded-md bg-primary text-primary-foreground",
  today: "font-bold ring-1 ring-ring",
  outside: "text-muted-foreground opacity-50",
  disabled: "opacity-40",
} as const;
