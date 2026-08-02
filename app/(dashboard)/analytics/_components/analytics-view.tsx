"use client";

import { motion } from "framer-motion";
import dynamic from "next/dynamic";
import { useMemo, useState } from "react";

import { LiveRegion, Skeleton } from "@/components/feedback";
import { PageContainer, PageHeader, Stack } from "@/components/layout";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";
import { analyticsService } from "@/lib/services";

import { AnalyticsFiltersBar } from "./analytics-filters-bar";
import { AnalyticsSummaryCards } from "./analytics-summary-cards";
import { InsightsPanel } from "./insights-panel";
import { PerformanceSection } from "./performance-section";
import { TopPostsTable } from "./top-posts-table";
import { useAnalyticsFilters } from "./use-analytics-filters";

const AnalyticsCharts = dynamic(
  () => import("./analytics-charts").then((module) => module.AnalyticsCharts),
  { loading: () => <Skeleton className="h-96 w-full rounded-xl" /> },
);

export function AnalyticsView(): React.JSX.Element {
  const { filters, dateLabel, setPlatform, setDateRange } = useAnalyticsFilters();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const summary = useMemo(() => analyticsService.computeSummary(filters), [filters]);
  const publishingTrend = useMemo(() => analyticsService.getPublishingTrend(filters), [filters]);
  const engagementByPlatform = useMemo(
    () => analyticsService.getEngagementByPlatform(filters),
    [filters],
  );
  const reachByPlatform = useMemo(() => analyticsService.getReachByPlatform(filters), [filters]);
  const aiUsageTrend = useMemo(() => analyticsService.getAiUsageTrend(filters), [filters]);
  const topPosts = useMemo(() => analyticsService.getTopPosts(filters), [filters]);
  const worstPosts = useMemo(() => analyticsService.getWorstPosts(filters), [filters]);
  const platformComparison = useMemo(
    () => analyticsService.getPlatformComparison(filters),
    [filters],
  );
  const bestPostingTimes = useMemo(() => analyticsService.getBestPostingTimes(filters), [filters]);
  const contentTypePerformance = useMemo(
    () => analyticsService.getContentTypePerformance(filters),
    [filters],
  );
  const insights = useMemo(() => analyticsService.getInsights(filters), [filters]);

  const tablePosts = useMemo(
    () => [...analyticsService.filterPosts(filters)].sort((a, b) => b.reach - a.reach),
    [filters],
  );

  const handleRefresh = (): void => {
    setIsRefreshing(true);
    window.setTimeout(() => setIsRefreshing(false), 500);
  };

  return (
    <PageContainer className="pb-8">
      <Stack gap="lg">
        <PageHeader
          title="Analytics"
          description="Actionable insights into content performance across all connected platforms."
        />

        <AnalyticsFiltersBar
          filters={filters}
          dateLabel={dateLabel}
          onDateRangeChange={setDateRange}
          onPlatformChange={setPlatform}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
        />

        {isRefreshing ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            {Array.from({ length: 6 }, (_, index) => (
              <Skeleton key={index} className="h-28 rounded-xl" />
            ))}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: MOTION_DURATION.page, ease: MOTION_EASING.enter }}
          >
            <AnalyticsSummaryCards summary={summary} />
          </motion.div>
        )}

        <section aria-labelledby="main-analytics-heading">
          <h2 id="main-analytics-heading" className="text-heading-2 mb-4">
            Main analytics
          </h2>
          {isRefreshing ? (
            <Skeleton className="h-96 w-full rounded-xl" />
          ) : (
            <AnalyticsCharts
              publishingTrend={publishingTrend}
              engagementByPlatform={engagementByPlatform}
              reachByPlatform={reachByPlatform}
              aiUsageTrend={aiUsageTrend}
              periodLabel={dateLabel}
            />
          )}
        </section>

        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(280px,340px)]">
          <div className="grid gap-4">
            <PerformanceSection
              topPosts={topPosts}
              worstPosts={worstPosts}
              platformComparison={platformComparison}
              bestPostingTimes={bestPostingTimes}
              contentTypePerformance={contentTypePerformance}
              periodLabel={dateLabel}
            />
            <TopPostsTable
              title="All top posts"
              description="Full performance table for the selected period."
              posts={tablePosts}
              emptyMessage="No posts match your filters."
            />
          </div>
          <InsightsPanel insights={insights} />
        </div>
      </Stack>

      <LiveRegion>Analytics updated for {dateLabel}</LiveRegion>
    </PageContainer>
  );
}
