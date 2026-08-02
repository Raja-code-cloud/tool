import type { LucideIcon } from "lucide-react";
import { AlertTriangle, BarChart3, CalendarClock, CheckCircle2 } from "lucide-react";

import type {
  ActivityItem,
  AgendaEntry,
  DashboardStorage,
  DashboardSuggestion,
  PlatformHealth,
  RecentContentRow,
} from "@/lib/domain/dashboard";

export type {
  ActivityItem,
  AgendaEntry,
  DashboardStorage,
  PlatformHealth,
  RecentContentRow,
} from "@/lib/domain/dashboard";

/** Dashboard-specific suggestion type (distinct from AI Studio suggestions). */
export type { DashboardSuggestion as AiSuggestion } from "@/lib/domain/dashboard";

export type DashboardStat = {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly comparison: string;
  readonly trend: string;
  readonly trendDirection: "up" | "down" | "neutral";
  readonly icon: LucideIcon;
  readonly variant?: "default" | "warning" | "danger";
};

export const DASHBOARD_STATS: readonly DashboardStat[] = [
  {
    id: "published",
    label: "Published this week",
    value: "42",
    comparison: "vs 36 last week",
    trend: "+16.7%",
    trendDirection: "up",
    icon: CheckCircle2,
  },
  {
    id: "scheduled",
    label: "Scheduled",
    value: "18",
    comparison: "6 publishing today",
    trend: "+3",
    trendDirection: "up",
    icon: CalendarClock,
  },
  {
    id: "engagement",
    label: "Engagement rate",
    value: "4.8%",
    comparison: "across all channels",
    trend: "+0.6 pts",
    trendDirection: "up",
    icon: BarChart3,
  },
  {
    id: "attention",
    label: "Needs attention",
    value: "3",
    comparison: "2 failed · 1 disconnected",
    trend: "Action required",
    trendDirection: "neutral",
    icon: AlertTriangle,
    variant: "warning",
  },
];

export const AI_SUGGESTIONS: readonly DashboardSuggestion[] = [
  {
    id: "s-1",
    title: "Finish LinkedIn variants for Q3 launch brief",
    reason: "Master article is approved but 2 platform variants are missing.",
    priority: "high",
    actionLabel: "Open in AI Studio",
    href: "/ai-studio",
  },
  {
    id: "s-2",
    title: "Re-authorise LinkedIn connection",
    reason: "Token expires in 3 days; scheduled posts will fail without renewal.",
    priority: "high",
    actionLabel: "Connect account",
    href: "/social-accounts",
  },
  {
    id: "s-3",
    title: "Fill calendar gap on Thursday",
    reason: "No posts scheduled between 10:00 and 16:00 IST.",
    priority: "medium",
    actionLabel: "Open scheduler",
    href: "/scheduler",
  },
  {
    id: "s-4",
    title: "Boost underperforming reel",
    reason: "Spring Launch Reel 02 reached 18% below the 30-day average.",
    priority: "low",
    actionLabel: "View analytics",
    href: "/analytics",
  },
];

export const TODAY_AGENDA: readonly AgendaEntry[] = [
  {
    id: "a-1",
    time: "09:30",
    title: "Product teaser — carousel",
    platform: "Instagram",
    status: "published",
  },
  {
    id: "a-2",
    time: "12:00",
    title: "Founder note — long form",
    platform: "LinkedIn",
    status: "queued",
  },
  {
    id: "a-3",
    time: "15:45",
    title: "Behind the scenes reel",
    platform: "TikTok",
    status: "queued",
  },
  { id: "a-4", time: "18:00", title: "Weekly roundup thread", platform: "X", status: "failed" },
];

export const RECENT_CONTENT: readonly RecentContentRow[] = [
  {
    id: "c-1",
    title: "Spring Launch — Reel 02",
    type: "Video",
    variants: 4,
    platforms: ["Instagram", "TikTok"],
    status: "published",
    owner: "Aarav Mehta",
    updatedAt: "2026-08-02T07:40:00.000Z",
  },
  {
    id: "c-2",
    title: "Q3 thought leadership article",
    type: "Article",
    variants: 3,
    platforms: ["LinkedIn", "Blog"],
    status: "review",
    owner: "Priya Nair",
    updatedAt: "2026-08-02T06:15:00.000Z",
  },
  {
    id: "c-3",
    title: "Feature highlight poster",
    type: "Image",
    variants: 6,
    platforms: ["Instagram", "Facebook", "LinkedIn"],
    status: "scheduled",
    owner: "Aarav Mehta",
    updatedAt: "2026-08-01T18:22:00.000Z",
  },
  {
    id: "c-4",
    title: "Customer story — Acme Corp",
    type: "Video",
    variants: 2,
    platforms: ["YouTube"],
    status: "failed",
    owner: "Marcus Lee",
    updatedAt: "2026-08-01T14:05:00.000Z",
  },
  {
    id: "c-5",
    title: "Newsletter intro block",
    type: "Article",
    variants: 1,
    platforms: ["Email"],
    status: "draft",
    owner: "Priya Nair",
    updatedAt: "2026-07-31T11:30:00.000Z",
  },
];

export const RECENT_ACTIVITY: readonly ActivityItem[] = [
  {
    id: "act-1",
    actor: "Aarav Mehta",
    action: "published",
    target: "Spring Launch — Reel 02",
    occurredAt: "2026-08-02T07:40:00.000Z",
  },
  {
    id: "act-2",
    actor: "System",
    action: "flagged",
    target: "Weekly roundup thread",
    occurredAt: "2026-08-02T06:02:00.000Z",
  },
  {
    id: "act-3",
    actor: "Priya Nair",
    action: "submitted for review",
    target: "Q3 thought leadership article",
    occurredAt: "2026-08-02T06:15:00.000Z",
  },
  {
    id: "act-4",
    actor: "AI Studio",
    action: "generated 6 variants for",
    target: "Feature highlight poster",
    occurredAt: "2026-08-01T17:48:00.000Z",
  },
];

export const PLATFORM_HEALTH: readonly PlatformHealth[] = [
  { id: "p-ig", name: "Instagram", status: "healthy", detail: "Publishing normally" },
  { id: "p-li", name: "LinkedIn", status: "warning", detail: "Token expires in 3 days" },
  { id: "p-tt", name: "TikTok", status: "healthy", detail: "Publishing normally" },
  { id: "p-x", name: "X", status: "error", detail: "Last post failed — rate limit" },
  { id: "p-yt", name: "YouTube", status: "healthy", detail: "Publishing normally" },
];

export const DASHBOARD_STORAGE: DashboardStorage = {
  usedBytes: 412_316_860_416,
  totalBytes: 1_099_511_627_776,
  label: "Media library",
};

export const WORKSPACE_HEALTH_SUMMARY = "All systems operational · 1 account needs attention";
