import type { HTMLAttributes, ReactNode } from "react";
import { AlertCircle, CheckCircle2, Info, TriangleAlert } from "lucide-react";

import { cn } from "../../lib/utils/cn";
import { Button } from "../ui";

export type AlertVariant = "info" | "success" | "warning" | "danger";
export type AlertProps = HTMLAttributes<HTMLDivElement> & { variant?: AlertVariant; title: string; action?: ReactNode };
export function Alert({ variant = "info", title, action, children, className, ...props }: AlertProps): React.JSX.Element {
  const Icon = variant === "success" ? CheckCircle2 : variant === "warning" ? TriangleAlert : variant === "danger" ? AlertCircle : Info;
  return <div role={variant === "danger" ? "alert" : "status"} className={cn("flex gap-3 rounded-lg border p-4", variant === "info" && "border-info/40 bg-info/10", variant === "success" && "border-success/40 bg-success/10", variant === "warning" && "border-warning/40 bg-warning/10", variant === "danger" && "border-destructive/40 bg-destructive/10", className)} {...props}><Icon className="mt-0.5 size-5 shrink-0" aria-hidden="true" /><div className="min-w-0 flex-1"><p className="text-heading-3">{title}</p>{children && <div className="mt-1 text-body text-muted-foreground">{children}</div>}{action && <div className="mt-3">{action}</div>}</div></div>;
}

export type EmptyStateProps = HTMLAttributes<HTMLDivElement> & { title: string; description: string; icon?: ReactNode; action?: ReactNode };
export function EmptyState({ title, description, icon, action, className, ...props }: EmptyStateProps): React.JSX.Element {
  return <div className={cn("grid min-h-64 place-items-center rounded-xl border border-dashed bg-card p-8 text-center", className)} {...props}><div className="max-w-md">{icon && <div className="mx-auto mb-4 grid size-12 place-items-center rounded-full bg-muted text-muted-foreground [&_svg]:size-5">{icon}</div>}<h2 className="text-heading-2">{title}</h2><p className="mt-2 text-body text-muted-foreground">{description}</p>{action && <div className="mt-5 flex flex-wrap justify-center gap-2">{action}</div>}</div></div>;
}

export type ErrorStateProps = EmptyStateProps & { onRetry?: () => void };
export function ErrorState({ onRetry, action, ...props }: ErrorStateProps): React.JSX.Element {
  return <EmptyState icon={<AlertCircle aria-hidden="true" />} action={action ?? (onRetry ? <Button variant="secondary" onClick={onRetry}>Try again</Button> : undefined)} {...props} />;
}

export type SkeletonProps = HTMLAttributes<HTMLDivElement>;
export function Skeleton({ className, ...props }: SkeletonProps): React.JSX.Element {
  return <div aria-hidden="true" className={cn("animate-pulse rounded-md bg-muted motion-reduce:animate-none", className)} {...props} />;
}

export type SkeletonTextProps = HTMLAttributes<HTMLDivElement> & { lines?: number };
/** Stacked text placeholders; the final line is shortened like real prose. */
export function SkeletonText({ lines = 3, className, ...props }: SkeletonTextProps): React.JSX.Element {
  return <div className={cn("grid gap-2", className)} {...props}>{Array.from({ length: lines }, (_, index) => <Skeleton key={index} className={cn("h-4", index === lines - 1 && lines > 1 && "w-3/5")} />)}</div>;
}

export type SkeletonCardProps = HTMLAttributes<HTMLDivElement> & { hasMedia?: boolean };
export function SkeletonCard({ hasMedia = false, className, ...props }: SkeletonCardProps): React.JSX.Element {
  return <div className={cn("rounded-xl border bg-card p-5", className)} {...props}>{hasMedia && <Skeleton className="mb-4 h-32 w-full" />}<Skeleton className="h-4 w-24" /><Skeleton className="mt-3 h-7 w-32" /><Skeleton className="mt-3 h-3 w-20" /></div>;
}

export type SkeletonTableProps = HTMLAttributes<HTMLDivElement> & { rows?: number; columns?: number };
export function SkeletonTable({ rows = 5, columns = 4, className, ...props }: SkeletonTableProps): React.JSX.Element {
  return <div className={cn("overflow-hidden rounded-lg border", className)} {...props}>
    <div className="flex gap-4 border-b bg-muted px-4 py-3">{Array.from({ length: columns }, (_, index) => <Skeleton key={index} className="h-3 flex-1" />)}</div>
    <div className="divide-y">{Array.from({ length: rows }, (_, rowIndex) => <div key={rowIndex} className="flex gap-4 bg-card px-4 py-3.5">{Array.from({ length: columns }, (_, columnIndex) => <Skeleton key={columnIndex} className="h-4 flex-1" />)}</div>)}</div>
  </div>;
}

export type SpinnerProps = HTMLAttributes<HTMLSpanElement> & { label?: string };
export function Spinner({ label = "Loading", className, ...props }: SpinnerProps): React.JSX.Element {
  return <span role="status" className={cn("inline-flex items-center gap-2", className)} {...props}><span className="size-4 animate-spin rounded-full border-2 border-current border-r-transparent motion-reduce:animate-none" aria-hidden="true" /><span className="sr-only">{label}</span></span>;
}

export type ProgressProps = HTMLAttributes<HTMLDivElement> & { value: number; label: string };
export function Progress({ value, label, className, ...props }: ProgressProps): React.JSX.Element {
  const bounded = Math.min(100, Math.max(0, value));
  return <div className={cn("grid gap-1.5", className)} {...props}><div className="flex justify-between text-xs"><span>{label}</span><span className="tabular-nums">{bounded}%</span></div><progress className="h-2 w-full accent-primary" max={100} value={bounded}>{bounded}%</progress></div>;
}

export type LiveRegionProps = HTMLAttributes<HTMLDivElement> & { politeness?: "polite" | "assertive" };
export function LiveRegion({ politeness = "polite", className, ...props }: LiveRegionProps): React.JSX.Element {
  return <div aria-live={politeness} aria-atomic="true" className={cn("sr-only", className)} {...props} />;
}

export type LoadingOverlayProps = HTMLAttributes<HTMLDivElement> & { label?: string; isVisible?: boolean };
export function LoadingOverlay({ label = "Loading", isVisible = true, className, ...props }: LoadingOverlayProps): React.JSX.Element | null {
  if (!isVisible) return null;
  return <div role="status" aria-label={label} className={cn("absolute inset-0 z-20 grid place-items-center bg-background/75 backdrop-blur-sm", className)} {...props}><Spinner label={label} /></div>;
}
