"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { BarChart, ChartFrame, ChartLegend } from "@/components/charts";
import { formatCompactNumber } from "@/lib/utils/analytics";
import { formatNumber } from "@/lib/utils/formatting";

export type AnalyticsChartsProps = {
  publishingTrend: readonly { date: string; posts: number; reach: number }[];
  engagementByPlatform: readonly { label: string; value: number }[];
  reachByPlatform: readonly { label: string; reach: number; color: string }[];
  aiUsageTrend: readonly { date: string; generated: number; approved: number }[];
  periodLabel: string;
};

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: readonly { value: number; name: string; color?: string }[];
  label?: string;
}): React.JSX.Element | null {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-popover shadow-popover rounded-lg border px-3 py-2 text-xs">
      {label && <p className="mb-1 font-semibold">{label}</p>}
      {payload.map((entry) => (
        <p key={entry.name} style={{ color: entry.color }}>
          {entry.name}: {formatNumber(entry.value)}
        </p>
      ))}
    </div>
  );
}

export function AnalyticsCharts({
  publishingTrend,
  engagementByPlatform,
  reachByPlatform,
  aiUsageTrend,
  periodLabel,
}: AnalyticsChartsProps): React.JSX.Element {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <ChartFrame
        title="Publishing trend"
        period={periodLabel}
        summary="Line chart showing posts published and reach over time."
      >
        <div className="h-64 w-full" aria-hidden="false">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={[...publishingTrend]}
              margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 11 }}
                tickFormatter={formatCompactNumber}
              />
              <Tooltip content={<ChartTooltip />} />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="posts"
                name="Posts"
                stroke="var(--chart-1)"
                strokeWidth={2}
                dot={false}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="reach"
                name="Reach"
                stroke="var(--chart-2)"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <ChartLegend
          items={[
            { label: "Posts", colorClassName: "bg-[var(--chart-1)]" },
            { label: "Reach", colorClassName: "bg-[var(--chart-2)]" },
          ]}
        />
      </ChartFrame>

      <ChartFrame
        title="Engagement by platform"
        period={periodLabel}
        summary="Horizontal bar chart comparing engagement across platforms."
      >
        <BarChart data={engagementByPlatform} valueFormatter={formatCompactNumber} />
      </ChartFrame>

      <ChartFrame
        title="Reach by platform"
        period={periodLabel}
        summary="Pie chart showing reach distribution by platform."
      >
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={[...reachByPlatform]}
                dataKey="reach"
                nameKey="label"
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
              >
                {reachByPlatform.map((entry) => (
                  <Cell key={entry.label} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => formatCompactNumber(value)} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <ChartLegend
          items={reachByPlatform.map((entry) => ({
            label: entry.label,
            colorClassName: "bg-primary",
          }))}
        />
      </ChartFrame>

      <ChartFrame
        title="AI usage trend"
        period={periodLabel}
        summary="Area chart showing AI-generated and approved content over time."
      >
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={[...aiUsageTrend]} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip content={<ChartTooltip />} />
              <Area
                type="monotone"
                dataKey="generated"
                name="Generated"
                stroke="var(--chart-3)"
                fill="var(--chart-3)"
                fillOpacity={0.25}
              />
              <Area
                type="monotone"
                dataKey="approved"
                name="Approved"
                stroke="var(--chart-4)"
                fill="var(--chart-4)"
                fillOpacity={0.25}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <ChartLegend
          items={[
            { label: "Generated", colorClassName: "bg-[var(--chart-3)]" },
            { label: "Approved", colorClassName: "bg-[var(--chart-4)]" },
          ]}
        />
      </ChartFrame>
    </div>
  );
}
