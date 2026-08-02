"use client";

import { CalendarPlus, Copy, ExternalLink, MoreHorizontal, Pencil } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { DataTable, SortButton, type DataTableColumn } from "@/components/tables";
import {
  Button,
  Checkbox,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui";
import { ROUTES } from "@/constants/navigation";
import type { ContentItem } from "@/lib/domain/content";
import {
  contentTypeAbbreviation,
  formatContentType,
  thumbnailGradient,
} from "@/lib/utils/content-display";
import { formatDate } from "@/lib/utils/formatting";

import { ContentStatusBadge } from "./content-status-badge";

export type SortField = "title" | "type" | "status" | "created" | "updated" | "author";
export type SortDirection = "ascending" | "descending" | "none";

export type ContentListViewProps = {
  items: readonly ContentItem[];
  selectedIds: ReadonlySet<string>;
  onToggleSelect: (id: string, checked: boolean) => void;
  onToggleSelectAll: (checked: boolean) => void;
  onSelect: (item: ContentItem) => void;
  sortField: SortField;
  sortDirection: SortDirection;
  onSort: (field: SortField) => void;
};

function sortDirectionFor(
  field: SortField,
  activeField: SortField,
  direction: SortDirection,
): SortDirection {
  return activeField === field ? direction : "none";
}

export function ContentListView({
  items,
  selectedIds,
  onToggleSelect,
  onToggleSelectAll,
  onSelect,
  sortField,
  sortDirection,
  onSort,
}: ContentListViewProps): React.JSX.Element {
  const allSelected = items.length > 0 && items.every((item) => selectedIds.has(item.id));
  const someSelected = items.some((item) => selectedIds.has(item.id));

  const columns = React.useMemo<readonly DataTableColumn<ContentItem>[]>(
    () => [
      {
        id: "select",
        header: (
          <Checkbox
            checked={allSelected ? true : someSelected ? "indeterminate" : false}
            onCheckedChange={(checked) => onToggleSelectAll(checked === true)}
            aria-label="Select all on this page"
          />
        ),
        cell: (row) => (
          <Checkbox
            checked={selectedIds.has(row.id)}
            onCheckedChange={(checked) => onToggleSelect(row.id, checked === true)}
            aria-label={`Select ${row.title}`}
          />
        ),
        className: "w-10",
      },
      {
        id: "thumbnail",
        header: <span className="sr-only">Thumbnail</span>,
        cell: (row) => (
          <div
            className="grid size-10 place-items-center rounded-md text-[10px] font-bold text-white"
            style={{ background: thumbnailGradient(row.thumbnailHue) }}
            aria-hidden="true"
          >
            {contentTypeAbbreviation(row.type)}
          </div>
        ),
        className: "w-12",
      },
      {
        id: "title",
        header: (
          <SortButton
            direction={sortDirectionFor("title", sortField, sortDirection)}
            onClick={() => onSort("title")}
          >
            Title
          </SortButton>
        ),
        isPrimary: true,
        cell: (row) => (
          <button
            type="button"
            className="focus-visible:ring-ring max-w-xs truncate text-left font-medium hover:underline focus-visible:ring-2 focus-visible:outline-none"
            onClick={() => onSelect(row)}
          >
            {row.title}
          </button>
        ),
      },
      {
        id: "type",
        header: (
          <SortButton
            direction={sortDirectionFor("type", sortField, sortDirection)}
            onClick={() => onSort("type")}
          >
            Type
          </SortButton>
        ),
        cell: (row) => formatContentType(row.type),
      },
      {
        id: "platforms",
        header: "Platforms",
        cell: (row) => <span className="text-muted-foreground">{row.platforms.join(", ")}</span>,
      },
      {
        id: "status",
        header: (
          <SortButton
            direction={sortDirectionFor("status", sortField, sortDirection)}
            onClick={() => onSort("status")}
          >
            Status
          </SortButton>
        ),
        cell: (row) => <ContentStatusBadge status={row.status} />,
      },
      {
        id: "created",
        header: (
          <SortButton
            direction={sortDirectionFor("created", sortField, sortDirection)}
            onClick={() => onSort("created")}
          >
            Created
          </SortButton>
        ),
        cell: (row) => (
          <time dateTime={row.createdAt}>{formatDate(row.createdAt, { dateStyle: "medium" })}</time>
        ),
      },
      {
        id: "updated",
        header: (
          <SortButton
            direction={sortDirectionFor("updated", sortField, sortDirection)}
            onClick={() => onSort("updated")}
          >
            Updated
          </SortButton>
        ),
        cell: (row) => (
          <time dateTime={row.updatedAt}>{formatDate(row.updatedAt, { dateStyle: "medium" })}</time>
        ),
      },
      {
        id: "author",
        header: (
          <SortButton
            direction={sortDirectionFor("author", sortField, sortDirection)}
            onClick={() => onSort("author")}
          >
            Author
          </SortButton>
        ),
        cell: (row) => row.author,
      },
      {
        id: "actions",
        header: <span className="sr-only">Actions</span>,
        align: "right",
        cell: (row) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="compact" aria-label={`Actions for ${row.title}`}>
                <MoreHorizontal aria-hidden="true" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onSelect={() => onSelect(row)}>
                <ExternalLink className="size-4" aria-hidden="true" />
                Open
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Pencil className="size-4" aria-hidden="true" />
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Copy className="size-4" aria-hidden="true" />
                Duplicate
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href={ROUTES.scheduler}>
                  <CalendarPlus className="size-4" aria-hidden="true" />
                  Schedule
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem isDestructive>Delete</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ),
      },
    ],
    [
      allSelected,
      someSelected,
      onToggleSelectAll,
      selectedIds,
      onToggleSelect,
      onSelect,
      sortField,
      sortDirection,
      onSort,
    ],
  );

  return (
    <DataTable
      caption="Content library items"
      columns={columns}
      rows={items}
      getRowId={(row) => row.id}
      density="compact"
      empty="No content matches your filters."
    />
  );
}
