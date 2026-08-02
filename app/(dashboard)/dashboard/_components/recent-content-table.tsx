import Link from "next/link";

import { Card, CardHeader } from "@/components/cards";
import { StatusBadge } from "@/components/feedback";
import { DataTable, type DataTableColumn } from "@/components/tables";
import { Button } from "@/components/ui";
import { ROUTES } from "@/constants/navigation";
import type { RecentContentRow } from "@/lib/domain/dashboard";
import { formatDate } from "@/lib/utils/formatting";

const CONTENT_STATUS = {
  draft: { variant: "neutral" as const, label: "Draft" },
  review: { variant: "warning" as const, label: "In review" },
  scheduled: { variant: "info" as const, label: "Scheduled" },
  published: { variant: "success" as const, label: "Published" },
  failed: { variant: "danger" as const, label: "Failed" },
};

const columns: readonly DataTableColumn<RecentContentRow>[] = [
  {
    id: "title",
    header: "Title",
    isPrimary: true,
    cell: (row) => (
      <div className="flex min-w-48 items-center gap-3">
        <span
          aria-hidden="true"
          className="bg-muted text-muted-foreground grid size-10 shrink-0 place-items-center rounded-md text-xs font-semibold"
        >
          {row.type.slice(0, 2).toUpperCase()}
        </span>
        <div className="min-w-0">
          <p className="truncate font-medium">{row.title}</p>
          <p className="text-small text-muted-foreground">{row.type}</p>
        </div>
      </div>
    ),
  },
  {
    id: "variants",
    header: "Variants",
    cell: (row) => <span className="tabular-nums">{row.variants}</span>,
  },
  {
    id: "platforms",
    header: "Platforms",
    cell: (row) => <span className="text-muted-foreground">{row.platforms.join(", ")}</span>,
  },
  {
    id: "status",
    header: "Status",
    cell: (row) => (
      <StatusBadge variant={CONTENT_STATUS[row.status].variant}>
        {CONTENT_STATUS[row.status].label}
      </StatusBadge>
    ),
  },
  {
    id: "owner",
    header: "Owner",
    cell: (row) => row.owner,
  },
  {
    id: "updated",
    header: "Updated",
    cell: (row) => (
      <time dateTime={row.updatedAt}>
        {formatDate(row.updatedAt, { dateStyle: "medium", timeStyle: "short" })}
      </time>
    ),
  },
  {
    id: "actions",
    header: <span className="sr-only">Actions</span>,
    align: "right",
    cell: () => (
      <Button asChild variant="ghost" size="compact">
        <Link href={ROUTES.contentLibrary}>View</Link>
      </Button>
    ),
  },
];

type RecentContentTableProps = {
  readonly rows: readonly RecentContentRow[];
};

export function RecentContentTable({ rows }: RecentContentTableProps): React.JSX.Element {
  return (
    <Card as="section" aria-labelledby="recent-content-heading">
      <CardHeader
        title="Recent content"
        description="Latest assets across your workspace."
        headingLevel={2}
        headingId="recent-content-heading"
        action={
          <Button asChild variant="secondary" size="compact">
            <Link href={ROUTES.contentLibrary}>Open library</Link>
          </Button>
        }
      />
      <DataTable
        caption="Recent content in the workspace"
        columns={columns}
        rows={rows}
        getRowId={(row) => row.id}
        empty="No content yet. Upload your first asset to get started."
      />
    </Card>
  );
}
