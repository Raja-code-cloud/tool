import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "../../lib/utils/cn";

export type DataTableColumn<T> = {
  id: string;
  header: ReactNode;
  cell: (row: T) => ReactNode;
  align?: "left" | "right";
  isPrimary?: boolean;
  className?: string;
};
export type DataTableProps<T> = {
  caption: string;
  columns: readonly DataTableColumn<T>[];
  rows: readonly T[];
  getRowId: (row: T) => string;
  empty?: ReactNode;
  className?: string;
  density?: "compact" | "default";
};
export function DataTable<T>({
  caption,
  columns,
  rows,
  getRowId,
  empty = "No results.",
  className,
  density = "default",
}: DataTableProps<T>): React.JSX.Element {
  if (rows.length === 0)
    return (
      <div
        className={cn(
          "bg-card text-muted-foreground rounded-lg border p-8 text-center text-sm",
          className,
        )}
        role="status"
      >
        {empty}
      </div>
    );
  return (
    <div className={cn("overflow-x-auto rounded-lg border", className)}>
      <table className="w-full border-collapse text-sm">
        <caption className="sr-only">{caption}</caption>
        <thead className="bg-muted sticky top-0 z-10">
          <tr>
            {columns.map((column) => (
              <th
                key={column.id}
                scope="col"
                className={cn(
                  "text-muted-foreground h-10 px-4 text-left text-xs font-semibold whitespace-nowrap",
                  column.align === "right" && "text-right",
                  column.className,
                )}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y">
          {rows.map((row) => (
            <tr key={getRowId(row)} className="bg-card hover:bg-accent/30">
              {columns.map((column) => (
                <td
                  key={column.id}
                  className={cn(
                    "px-4",
                    density === "compact" ? "h-11" : "h-13",
                    column.align === "right" && "text-right tabular-nums",
                    column.isPrimary && "sticky left-0 bg-inherit font-medium",
                    column.className,
                  )}
                >
                  {column.cell(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export type SortButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  direction?: "ascending" | "descending" | "none";
};
export function SortButton({
  direction = "none",
  children,
  className,
  ...props
}: SortButtonProps): React.JSX.Element {
  return (
    <button
      className={cn(
        "focus-visible:ring-ring inline-flex min-h-9 items-center gap-1 rounded px-1 focus-visible:ring-2 focus-visible:outline-none",
        className,
      )}
      {...props}
    >
      {children}
      <span aria-hidden="true">
        {direction === "ascending" ? "↑" : direction === "descending" ? "↓" : "↕"}
      </span>
      <span className="sr-only">{direction === "none" ? "Not sorted" : `Sorted ${direction}`}</span>
    </button>
  );
}

export type TableToolbarProps = HTMLAttributes<HTMLDivElement> & { label?: string };
export function TableToolbar({
  label = "Table controls",
  className,
  ...props
}: TableToolbarProps): React.JSX.Element {
  return (
    <div
      role="toolbar"
      aria-label={label}
      className={cn("flex min-h-11 flex-wrap items-center gap-2", className)}
      {...props}
    />
  );
}

export type EmptyTableStateProps = HTMLAttributes<HTMLDivElement> & {
  title?: string;
  description?: string;
  action?: ReactNode;
};
export function EmptyTableState({
  title = "No results",
  description,
  action,
  className,
  ...props
}: EmptyTableStateProps): React.JSX.Element {
  return (
    <div
      role="status"
      className={cn("bg-card rounded-lg border p-8 text-center", className)}
      {...props}
    >
      <p className="font-semibold">{title}</p>
      {description && <p className="text-muted-foreground mt-1 text-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
