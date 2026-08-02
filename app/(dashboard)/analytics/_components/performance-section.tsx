"use client";

import { Card, CardHeader } from "@/components/cards";
import { BarChart, ChartFrame } from "@/components/charts";
import { DataTable, type DataTableColumn } from "@/components/tables";
import type { AnalyticsPost } from "@/lib/domain/analytics";
import { formatCompactNumber, formatPercent } from "@/lib/utils/analytics";
import { formatNumber } from "@/lib/utils/formatting";

import { TopPostsTable } from "./top-posts-table";

export type PerformanceSectionProps = {
  topPosts: readonly AnalyticsPost[];
  worstPosts: readonly AnalyticsPost[];
  platformComparison: readonly {
    platform: string;
    label: string;
    reach: number;
    engagement: number;
    avgCtr: number;
    posts: number;
  }[];
  bestPostingTimes: readonly { label: string; value: number }[];
  contentTypePerformance: readonly { label: string; value: number; posts: number }[];
  periodLabel: string;
};

const comparisonColumns: readonly DataTableColumn<
  PerformanceSectionProps["platformComparison"][number]
>[] = [
  { id: "platform", header: "Platform", isPrimary: true, cell: (row) => row.label },
  { id: "reach", header: "Reach", align: "right", cell: (row) => formatCompactNumber(row.reach) },
  {
    id: "engagement",
    header: "Engagement",
    align: "right",
    cell: (row) => formatCompactNumber(row.engagement),
  },
  { id: "ctr", header: "Avg CTR", align: "right", cell: (row) => formatPercent(row.avgCtr) },
  { id: "posts", header: "Posts", align: "right", cell: (row) => formatNumber(row.posts) },
];

export function PerformanceSection({
  topPosts,
  worstPosts,
  platformComparison,
  bestPostingTimes,
  contentTypePerformance,
  periodLabel,
}: PerformanceSectionProps): React.JSX.Element {
  return (
    <section aria-labelledby="performance-heading" className="grid gap-4">
      <h2 id="performance-heading" className="text-heading-2">
        Performance
      </h2>

      <div className="grid gap-4 xl:grid-cols-2">
        <TopPostsTable
          title="Top performing posts"
          description="Highest engagement rate in the selected period."
          posts={topPosts}
        />
        <TopPostsTable
          title="Lowest performing posts"
          description="Posts that may benefit from refreshed AI variants or rescheduling."
          posts={worstPosts}
        />
      </div>

      <Card as="section">
        <CardHeader
          title="Platform comparison"
          description="Normalized reach, engagement, and CTR by platform."
          headingLevel={3}
        />
        <DataTable
          caption="Platform comparison analytics"
          columns={comparisonColumns}
          rows={platformComparison}
          getRowId={(row) => row.platform}
          empty="No platform data for the selected filters."
          density="compact"
        />
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartFrame
          title="Best posting time"
          period={periodLabel}
          summary="Engagement by hour of day."
        >
          <BarChart data={bestPostingTimes} valueFormatter={formatCompactNumber} />
        </ChartFrame>
        <ChartFrame
          title="Content type performance"
          period={periodLabel}
          summary="Engagement by content format."
        >
          <BarChart
            data={contentTypePerformance.map((item) => ({ label: item.label, value: item.value }))}
            valueFormatter={formatCompactNumber}
          />
        </ChartFrame>
      </div>
    </section>
  );
}
