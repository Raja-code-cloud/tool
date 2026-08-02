import type { AnalyticsInsight, AnalyticsPost } from "@/lib/domain/analytics";
import type { PlatformId } from "@/lib/domain/platform";

export type { AnalyticsDateRange, AnalyticsInsight, AnalyticsPost } from "@/lib/domain/analytics";

export const ANALYTICS_DATE_RANGES = [
  { value: "today" as const, label: "Today", factor: 0.04 },
  { value: "7d" as const, label: "Last 7 days", factor: 0.22 },
  { value: "30d" as const, label: "Last 30 days", factor: 1 },
  { value: "90d" as const, label: "Last 90 days", factor: 2.85 },
  { value: "custom" as const, label: "Custom", factor: 1 },
];

export const ANALYTICS_PLATFORMS: readonly { value: PlatformId | "all"; label: string }[] = [
  { value: "all", label: "All platforms" },
  { value: "linkedin", label: "LinkedIn" },
  { value: "facebook", label: "Facebook" },
  { value: "instagram", label: "Instagram" },
  { value: "x", label: "X (Twitter)" },
  { value: "medium", label: "Medium" },
  { value: "youtube", label: "YouTube" },
];

export const ANALYTICS_BASE_SUMMARY = {
  totalPosts: 142,
  totalReach: 284500,
  totalEngagement: 18640,
  followersGrowth: 1240,
  scheduledPosts: 18,
  aiContentGenerated: 386,
} as const;

export const PUBLISHING_TREND = [
  { date: "Jul 6", posts: 3, reach: 8200 },
  { date: "Jul 10", posts: 5, reach: 12400 },
  { date: "Jul 14", posts: 4, reach: 9800 },
  { date: "Jul 18", posts: 6, reach: 15200 },
  { date: "Jul 22", posts: 5, reach: 13100 },
  { date: "Jul 26", posts: 7, reach: 17800 },
  { date: "Jul 30", posts: 4, reach: 11200 },
  { date: "Aug 2", posts: 8, reach: 21400 },
] as const;

export const ENGAGEMENT_BY_PLATFORM = [
  { platform: "linkedin" as const, label: "LinkedIn", engagement: 6240 },
  { platform: "youtube" as const, label: "YouTube", engagement: 4180 },
  { platform: "medium" as const, label: "Medium", engagement: 3520 },
  { platform: "instagram" as const, label: "Instagram", engagement: 2180 },
  { platform: "x" as const, label: "X (Twitter)", engagement: 1640 },
  { platform: "facebook" as const, label: "Facebook", engagement: 880 },
];

export const REACH_BY_PLATFORM = [
  { platform: "linkedin" as const, label: "LinkedIn", reach: 98500, color: "var(--chart-1)" },
  { platform: "youtube" as const, label: "YouTube", reach: 72400, color: "var(--chart-2)" },
  { platform: "medium" as const, label: "Medium", reach: 45200, color: "var(--chart-3)" },
  { platform: "instagram" as const, label: "Instagram", reach: 31800, color: "var(--chart-4)" },
  { platform: "x" as const, label: "X (Twitter)", reach: 24600, color: "var(--chart-5)" },
  { platform: "facebook" as const, label: "Facebook", reach: 12000, color: "var(--chart-6)" },
];

export const AI_USAGE_TREND = [
  { date: "Jul 6", generated: 18, approved: 14 },
  { date: "Jul 10", generated: 24, approved: 20 },
  { date: "Jul 14", generated: 22, approved: 18 },
  { date: "Jul 18", generated: 31, approved: 26 },
  { date: "Jul 22", generated: 28, approved: 24 },
  { date: "Jul 26", generated: 35, approved: 30 },
  { date: "Jul 30", generated: 29, approved: 25 },
  { date: "Aug 2", generated: 42, approved: 36 },
] as const;

export const BEST_POSTING_TIMES = [
  { hour: "8 AM", engagement: 420 },
  { hour: "9 AM", engagement: 680 },
  { hour: "10 AM", engagement: 540 },
  { hour: "12 PM", engagement: 720 },
  { hour: "2 PM", engagement: 890 },
  { hour: "4 PM", engagement: 610 },
  { hour: "6 PM", engagement: 480 },
] as const;

export const CONTENT_TYPE_PERFORMANCE = [
  { type: "Deep-dive article", engagement: 4820, posts: 28 },
  { type: "Video walkthrough", engagement: 3960, posts: 18 },
  { type: "Thread / carousel", engagement: 2840, posts: 34 },
  { type: "Quick tip", engagement: 1620, posts: 42 },
  { type: "Case study", engagement: 5400, posts: 12 },
] as const;

export const ANALYTICS_POSTS: readonly AnalyticsPost[] = [
  {
    id: "p-1",
    title: "Azure Landing Zone Deep Dive",
    platform: "linkedin",
    contentType: "article",
    reach: 28400,
    likes: 842,
    comments: 126,
    shares: 94,
    ctr: 4.2,
    engagementRate: 3.7,
    publishedAt: "2026-07-28T14:00:00.000Z",
  },
  {
    id: "p-2",
    title: "Terraform Modules Best Practices",
    platform: "medium",
    contentType: "article",
    reach: 18200,
    likes: 620,
    comments: 48,
    shares: 112,
    ctr: 5.1,
    engagementRate: 4.3,
    publishedAt: "2026-07-25T10:00:00.000Z",
  },
  {
    id: "p-3",
    title: "Kubernetes Security Hardening Checklist",
    platform: "youtube",
    contentType: "video",
    reach: 35600,
    likes: 1240,
    comments: 186,
    shares: 320,
    ctr: 6.8,
    engagementRate: 4.9,
    publishedAt: "2026-07-22T16:00:00.000Z",
  },
  {
    id: "p-4",
    title: "Cloud Run Architecture Patterns",
    platform: "linkedin",
    contentType: "article",
    reach: 22100,
    likes: 540,
    comments: 72,
    shares: 58,
    ctr: 3.9,
    engagementRate: 3.1,
    publishedAt: "2026-07-20T09:00:00.000Z",
  },
  {
    id: "p-5",
    title: "IAM Best Practices Thread",
    platform: "x",
    contentType: "thread",
    reach: 12400,
    likes: 380,
    comments: 64,
    shares: 210,
    ctr: 2.8,
    engagementRate: 5.2,
    publishedAt: "2026-07-18T12:00:00.000Z",
  },
  {
    id: "p-6",
    title: "Cloud SQL HA Setup Guide",
    platform: "medium",
    contentType: "article",
    reach: 9800,
    likes: 290,
    comments: 34,
    shares: 42,
    ctr: 3.4,
    engagementRate: 3.8,
    publishedAt: "2026-07-15T11:00:00.000Z",
  },
  {
    id: "p-7",
    title: "DevOps Pipeline Automation Tips",
    platform: "instagram",
    contentType: "carousel",
    reach: 8600,
    likes: 420,
    comments: 28,
    shares: 86,
    ctr: 2.1,
    engagementRate: 6.2,
    publishedAt: "2026-07-12T15:00:00.000Z",
  },
  {
    id: "p-8",
    title: "FinOps Weekly: Cost Controls",
    platform: "linkedin",
    contentType: "article",
    reach: 19200,
    likes: 480,
    comments: 56,
    shares: 44,
    ctr: 3.6,
    engagementRate: 3.0,
    publishedAt: "2026-07-10T08:00:00.000Z",
  },
  {
    id: "p-9",
    title: "AKS Workload Identity Explained",
    platform: "youtube",
    contentType: "video",
    reach: 24800,
    likes: 890,
    comments: 142,
    shares: 198,
    ctr: 5.4,
    engagementRate: 4.2,
    publishedAt: "2026-07-08T14:00:00.000Z",
  },
  {
    id: "p-10",
    title: "Zero Trust Networking Basics",
    platform: "facebook",
    contentType: "article",
    reach: 4200,
    likes: 86,
    comments: 12,
    shares: 18,
    ctr: 1.8,
    engagementRate: 2.7,
    publishedAt: "2026-07-05T10:00:00.000Z",
  },
  {
    id: "p-11",
    title: "Platform Engineering 101",
    platform: "linkedin",
    contentType: "article",
    reach: 8400,
    likes: 180,
    comments: 22,
    shares: 14,
    ctr: 2.4,
    engagementRate: 2.6,
    publishedAt: "2026-07-03T09:00:00.000Z",
  },
  {
    id: "p-12",
    title: "Legacy Migration Pitfalls",
    platform: "medium",
    contentType: "article",
    reach: 5200,
    likes: 96,
    comments: 18,
    shares: 8,
    ctr: 1.9,
    engagementRate: 2.3,
    publishedAt: "2026-06-28T13:00:00.000Z",
  },
];

export const ANALYTICS_INSIGHTS: readonly AnalyticsInsight[] = [
  {
    id: "i-1",
    category: "recommendation",
    title: "Double down on LinkedIn deep-dives",
    description:
      "Azure and Terraform articles outperform other formats by 2.3× on LinkedIn. Schedule two more deep-dives this week.",
    priority: "high",
  },
  {
    id: "i-2",
    category: "opportunity",
    title: "Instagram carousel gap",
    description:
      "You have not published an Instagram carousel in 14 days. DevOps tip carousels historically earn 6%+ engagement.",
    priority: "medium",
  },
  {
    id: "i-3",
    category: "publishing",
    title: "Shift X threads to 12 PM ET",
    description: "Threads published at noon see 18% higher engagement than morning slots on X.",
    priority: "medium",
  },
  {
    id: "i-4",
    category: "summary",
    title: "Weekly performance summary",
    description:
      "Reach up 12%, engagement up 8%. YouTube and LinkedIn drove 71% of total engagement. 3 posts need AI variant refresh.",
    priority: "low",
  },
  {
    id: "i-5",
    category: "recommendation",
    title: "Refresh underperforming Facebook posts",
    description:
      "Facebook CTR is 1.8% vs 4.2% workspace average. Shorten copy and add stronger visual hooks.",
    priority: "high",
  },
  {
    id: "i-6",
    category: "opportunity",
    title: "Repurpose top YouTube content",
    description:
      "Kubernetes Security video has 4.9% engagement — create LinkedIn and Medium variants to extend reach.",
    priority: "high",
  },
];

export const PLATFORM_COMPARISON = [
  {
    platform: "linkedin" as const,
    label: "LinkedIn",
    reach: 98500,
    engagement: 6240,
    avgCtr: 3.8,
    posts: 48,
  },
  {
    platform: "youtube" as const,
    label: "YouTube",
    reach: 72400,
    engagement: 4180,
    avgCtr: 5.6,
    posts: 22,
  },
  {
    platform: "medium" as const,
    label: "Medium",
    reach: 45200,
    engagement: 3520,
    avgCtr: 4.1,
    posts: 26,
  },
  {
    platform: "instagram" as const,
    label: "Instagram",
    reach: 31800,
    engagement: 2180,
    avgCtr: 2.4,
    posts: 18,
  },
  {
    platform: "x" as const,
    label: "X (Twitter)",
    reach: 24600,
    engagement: 1640,
    avgCtr: 2.9,
    posts: 20,
  },
  {
    platform: "facebook" as const,
    label: "Facebook",
    reach: 12000,
    engagement: 880,
    avgCtr: 1.9,
    posts: 8,
  },
];
