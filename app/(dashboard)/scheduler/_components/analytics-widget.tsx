"use client";

import { MetricCard } from "@/components/cards";
import type { SchedulerAnalytics } from "@/lib/utils/scheduler";

export function AnalyticsWidget({
  analytics,
}: {
  analytics: SchedulerAnalytics;
}): React.JSX.Element {
  return (
    <div className="grid grid-cols-2 gap-2 xl:grid-cols-3">
      <MetricCard label="Posts today" value={analytics.postsToday} className="p-3" />
      <MetricCard label="This week" value={analytics.postsThisWeek} className="p-3" />
      <MetricCard label="Scheduled" value={analytics.scheduled} className="p-3" />
      <MetricCard label="Missed" value={analytics.missed} className="p-3" />
      <MetricCard label="Failed" value={analytics.failed} className="p-3" />
      <MetricCard label="Success rate" value={`${analytics.successRate}%`} className="p-3" />
    </div>
  );
}
