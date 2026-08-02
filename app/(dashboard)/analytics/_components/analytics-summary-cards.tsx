"use client";

import { BarChart3, CalendarClock, Eye, Heart, Sparkles, Users } from "lucide-react";

import { MetricCard } from "@/components/cards";
import { formatCompactNumber } from "@/lib/utils/analytics";
import { formatNumber } from "@/lib/utils/formatting";

export type AnalyticsSummaryCardsProps = {
  summary: {
    totalPosts: number;
    totalReach: number;
    totalEngagement: number;
    followersGrowth: number;
    scheduledPosts: number;
    aiContentGenerated: number;
  };
};

const CARDS = [
  { key: "totalPosts", label: "Total posts", icon: BarChart3, format: formatNumber },
  { key: "totalReach", label: "Total reach", icon: Eye, format: formatCompactNumber },
  { key: "totalEngagement", label: "Total engagement", icon: Heart, format: formatCompactNumber },
  {
    key: "followersGrowth",
    label: "Followers growth",
    icon: Users,
    format: (v: number) => `+${formatCompactNumber(v)}`,
  },
  { key: "scheduledPosts", label: "Scheduled posts", icon: CalendarClock, format: formatNumber },
  {
    key: "aiContentGenerated",
    label: "AI content generated",
    icon: Sparkles,
    format: formatNumber,
  },
] as const;

export function AnalyticsSummaryCards({ summary }: AnalyticsSummaryCardsProps): React.JSX.Element {
  return (
    <section aria-labelledby="analytics-summary-heading">
      <h2 id="analytics-summary-heading" className="sr-only">
        Analytics summary
      </h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {CARDS.map((card) => {
          const Icon = card.icon;
          const value = summary[card.key];
          return (
            <MetricCard
              key={card.key}
              label={card.label}
              value={card.format(value)}
              visualization={
                <span
                  aria-hidden="true"
                  className="bg-primary/15 text-primary grid size-10 place-items-center rounded-lg"
                >
                  <Icon className="size-5" />
                </span>
              }
            />
          );
        })}
      </div>
    </section>
  );
}
