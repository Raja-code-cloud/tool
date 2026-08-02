"use client";

import { Card, CardHeader } from "@/components/cards";
import { PlatformChip } from "@/components/platform";
import { DataTable, type DataTableColumn } from "@/components/tables";
import type { AnalyticsPost } from "@/lib/domain/analytics";
import { formatCompactNumber, formatPercent } from "@/lib/utils/analytics";
import { formatDate, formatNumber } from "@/lib/utils/formatting";

const columns: readonly DataTableColumn<AnalyticsPost>[] = [
  {
    id: "title",
    header: "Title",
    isPrimary: true,
    cell: (row) => <span className="font-medium">{row.title}</span>,
  },
  {
    id: "platform",
    header: "Platform",
    cell: (row) => <PlatformChip platform={row.platform} />,
  },
  {
    id: "reach",
    header: "Reach",
    align: "right",
    cell: (row) => formatCompactNumber(row.reach),
  },
  {
    id: "likes",
    header: "Likes",
    align: "right",
    cell: (row) => formatNumber(row.likes),
  },
  {
    id: "comments",
    header: "Comments",
    align: "right",
    cell: (row) => formatNumber(row.comments),
  },
  {
    id: "shares",
    header: "Shares",
    align: "right",
    cell: (row) => formatNumber(row.shares),
  },
  {
    id: "ctr",
    header: "CTR",
    align: "right",
    cell: (row) => formatPercent(row.ctr),
  },
  {
    id: "published",
    header: "Published",
    cell: (row) => (
      <time dateTime={row.publishedAt}>{formatDate(row.publishedAt, { dateStyle: "medium" })}</time>
    ),
  },
];

export type TopPostsTableProps = {
  title: string;
  description: string;
  posts: readonly AnalyticsPost[];
  emptyMessage?: string;
};

export function TopPostsTable({
  title,
  description,
  posts,
  emptyMessage = "No posts match your filters.",
}: TopPostsTableProps): React.JSX.Element {
  return (
    <Card as="section">
      <CardHeader title={title} description={description} headingLevel={3} />
      <DataTable
        caption={`${title} analytics table`}
        columns={columns}
        rows={posts}
        getRowId={(row) => row.id}
        empty={emptyMessage}
        density="compact"
      />
    </Card>
  );
}
