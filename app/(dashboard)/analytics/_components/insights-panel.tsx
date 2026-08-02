"use client";

import { Lightbulb, Sparkles, Target, TrendingUp } from "lucide-react";

import { Card, CardHeader } from "@/components/cards";
import { StatusBadge } from "@/components/feedback";
import type { AnalyticsInsight } from "@/lib/domain/analytics";

const CATEGORY_CONFIG = {
  recommendation: { label: "AI recommendation", icon: Sparkles, variant: "info" as const },
  opportunity: { label: "Engagement opportunity", icon: Target, variant: "success" as const },
  publishing: { label: "Publishing suggestion", icon: TrendingUp, variant: "warning" as const },
  summary: { label: "Weekly summary", icon: Lightbulb, variant: "neutral" as const },
};

const PRIORITY_VARIANT = {
  high: "danger",
  medium: "warning",
  low: "info",
} as const;

export type InsightsPanelProps = {
  insights: readonly AnalyticsInsight[];
};

export function InsightsPanel({ insights }: InsightsPanelProps): React.JSX.Element {
  return (
    <Card as="section" aria-labelledby="insights-heading" className="h-full">
      <CardHeader
        title="Insights"
        description="AI recommendations, opportunities, and publishing suggestions."
        headingLevel={2}
        headingId="insights-heading"
      />
      {insights.length === 0 ? (
        <p className="text-muted-foreground text-sm">No insights for the selected filters.</p>
      ) : (
        <ul className="grid gap-3">
          {insights.map((insight) => {
            const config = CATEGORY_CONFIG[insight.category];
            const Icon = config.icon;
            return (
              <li
                key={insight.id}
                className="bg-card hover:bg-accent/30 rounded-lg border p-4 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <Icon className="text-primary mt-0.5 size-4 shrink-0" aria-hidden="true" />
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="text-sm font-semibold">{insight.title}</p>
                      <StatusBadge variant={PRIORITY_VARIANT[insight.priority]}>
                        {insight.priority}
                      </StatusBadge>
                    </div>
                    <p className="text-muted-foreground mt-1 text-xs font-medium">{config.label}</p>
                    <p className="text-muted-foreground mt-2 text-sm">{insight.description}</p>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}
