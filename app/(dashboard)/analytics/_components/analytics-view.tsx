"use client";

import { motion } from "framer-motion";
import dynamic from "next/dynamic";
import { useMemo } from "react";

import { Alert, LiveRegion, Skeleton } from "@/components/feedback";
import { PageContainer, PageHeader, Stack } from "@/components/layout";
import { useAnalyticsData, useAnalyticsFiltersState } from "@/hooks/use-analytics-data";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";
import { downloadCsv, exportAnalyticsCsv } from "@/lib/services/analytics-api-service";

import { AnalyticsFiltersBar } from "./analytics-filters-bar";
import { AnalyticsSummaryCards } from "./analytics-summary-cards";
import { InsightsPanel } from "./insights-panel";
import { PerformanceSection } from "./performance-section";
import { TopPostsTable } from "./top-posts-table";

const AnalyticsCharts = dynamic(
  () => import("./analytics-charts").then((module) => module.AnalyticsCharts),
  { loading: () => <Skeleton className="h-96 w-full rounded-xl" /> },
);

export function AnalyticsView(): React.JSX.Element {
  const {
    filters,
    search,
    sort,
    cursor,
    refreshKey,
    setSearch,
    setSort,
    setCursor,
    refresh,
    setPlatform,
    setDateRange,
  } = useAnalyticsFiltersState();

  const tableControls = useMemo(
    () => ({ search, sort, cursor, limit: 50 }),
    [search, sort, cursor],
  );

  const {
    summary,
    publishingTrend,
    engagementByPlatform,
    reachByPlatform,
    aiUsageTrend,
    topPosts,
    worstPosts,
    platformComparison,
    bestPostingTimes,
    contentTypePerformance,
    insights,
    tablePosts,
    platformFilterOptions,
    pagination,
    partial,
    warnings,
    isLoading,
    isRefreshing,
    error,
    dateRangeOptions,
    reload,
  } = useAnalyticsData(filters, tableControls, refreshKey);

  const dateLabel = useMemo(() => {
    const option = dateRangeOptions.find((item) => item.value === filters.dateRange);
    return option?.label ?? filters.dateRange;
  }, [dateRangeOptions, filters.dateRange]);

  const chartEngagement = useMemo(
    () =>
      engagementByPlatform.map((item) => ({
        label: item.label,
        value: item.engagement,
      })),
    [engagementByPlatform],
  );

  const chartBestPostingTimes = useMemo(
    () =>
      bestPostingTimes.map((item) => ({
        label: item.hour,
        value: item.engagement,
      })),
    [bestPostingTimes],
  );

  const chartContentTypePerformance = useMemo(
    () =>
      contentTypePerformance.map((item) => ({
        label: item.type,
        value: item.engagement,
        posts: item.posts,
      })),
    [contentTypePerformance],
  );

  const handleRefresh = (): void => {
    refresh();
    void reload();
  };

  const handleExportCsv = (): void => {
    const csv = exportAnalyticsCsv(tablePosts);
    downloadCsv(`analytics-${filters.dateRange}.csv`, csv);
  };

  const showSkeleton = isLoading || isRefreshing;

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
          dateRangeOptions={dateRangeOptions}
          platformFilterOptions={platformFilterOptions}
          search={search}
          sort={sort}
          onSearchChange={setSearch}
          onSortChange={setSort}
          onDateRangeChange={setDateRange}
          onPlatformChange={setPlatform}
          onRefresh={handleRefresh}
          onExportCsv={handleExportCsv}
          isRefreshing={isRefreshing}
          canExport={tablePosts.length > 0}
        />

        {error && (
          <Alert variant="danger" title="Unable to load analytics">
            {error}
          </Alert>
        )}

        {partial && warnings.length > 0 && !error && (
          <Alert variant="warning" title="Partial analytics data">
            {warnings.join(" ")}
          </Alert>
        )}

        {showSkeleton ? (
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
          {showSkeleton ? (
            <Skeleton className="h-96 w-full rounded-xl" />
          ) : (
            <AnalyticsCharts
              publishingTrend={publishingTrend}
              engagementByPlatform={chartEngagement}
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
              bestPostingTimes={chartBestPostingTimes}
              contentTypePerformance={chartContentTypePerformance}
              periodLabel={dateLabel}
            />
            <TopPostsTable
              title="All top posts"
              description="Full performance table for the selected period."
              posts={tablePosts}
              emptyMessage="No posts match your filters."
              hasMore={pagination.hasMore}
              onLoadMore={() => setCursor(pagination.nextCursor)}
            />
          </div>
          <InsightsPanel insights={insights} />
        </div>
      </Stack>

      <LiveRegion>
        {error ? "Analytics failed to load." : `Analytics updated for ${dateLabel}`}
      </LiveRegion>
    </PageContainer>
  );
}
