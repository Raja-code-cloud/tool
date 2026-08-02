import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "../../lib/utils/cn";

export type ChartDatum = { label: string; value: number };
export type ChartFrameProps = HTMLAttributes<HTMLElement> & {
  title: string;
  period?: string;
  units?: string;
  summary: string;
  legend?: ReactNode;
};
export function ChartFrame({
  title,
  period,
  units,
  summary,
  legend,
  children,
  className,
  ...props
}: ChartFrameProps): React.JSX.Element {
  return (
    <figure
      className={cn("bg-card rounded-lg border p-5", className)}
      aria-labelledby={`${toId(title)}-title`}
      aria-describedby={`${toId(title)}-summary`}
      {...props}
    >
      <figcaption>
        <h3 id={`${toId(title)}-title`} className="font-semibold">
          {title}
        </h3>
        {(period || units) && (
          <p className="text-muted-foreground text-xs">
            {[period, units].filter(Boolean).join(" · ")}
          </p>
        )}
        <p id={`${toId(title)}-summary`} className="sr-only">
          {summary}
        </p>
      </figcaption>
      {legend}
      <div className="mt-4">{children}</div>
    </figure>
  );
}

export type ChartLegendItem = { label: string; colorClassName: string; symbol?: string };
export type ChartLegendProps = HTMLAttributes<HTMLUListElement> & {
  items: readonly ChartLegendItem[];
};
export function ChartLegend({ items, className, ...props }: ChartLegendProps): React.JSX.Element {
  return (
    <ul
      className={cn("text-muted-foreground mt-3 flex flex-wrap gap-4 text-xs", className)}
      {...props}
    >
      {items.map((item) => (
        <li key={item.label} className="flex items-center gap-1.5">
          <span className={cn("size-2.5 rounded-sm", item.colorClassName)} aria-hidden="true" />
          {item.symbol && <span className="sr-only">{item.symbol}</span>}
          {item.label}
        </li>
      ))}
    </ul>
  );
}

export type BarChartProps = HTMLAttributes<HTMLDivElement> & {
  data: readonly ChartDatum[];
  maximum?: number;
  valueFormatter?: (value: number) => string;
};
export function BarChart({
  data,
  maximum = Math.max(...data.map(({ value }) => value), 1),
  valueFormatter = String,
  className,
  ...props
}: BarChartProps): React.JSX.Element {
  return (
    <div className={cn("grid gap-3", className)} {...props}>
      {data.map((datum) => (
        <div
          key={datum.label}
          className="grid grid-cols-[minmax(5rem,1fr)_3fr_auto] items-center gap-3 text-xs"
        >
          <span className="truncate">{datum.label}</span>
          <div className="bg-muted h-3 overflow-hidden rounded-sm">
            <div
              className="bg-primary h-full"
              style={{ width: `${Math.min(100, Math.max(0, (datum.value / maximum) * 100))}%` }}
            />
          </div>
          <span className="tabular-nums">{valueFormatter(datum.value)}</span>
        </div>
      ))}
    </div>
  );
}

export type ChartDataTableProps = HTMLAttributes<HTMLTableElement> & {
  caption: string;
  data: readonly ChartDatum[];
  valueHeading?: string;
  valueFormatter?: (value: number) => string;
};
export function ChartDataTable({
  caption,
  data,
  valueHeading = "Value",
  valueFormatter = String,
  className,
  ...props
}: ChartDataTableProps): React.JSX.Element {
  return (
    <table className={cn("mt-4 w-full text-sm", className)} {...props}>
      <caption className="sr-only">{caption}</caption>
      <thead>
        <tr>
          <th className="border-b py-2 text-left">Category</th>
          <th className="border-b py-2 text-right">{valueHeading}</th>
        </tr>
      </thead>
      <tbody>
        {data.map((datum) => (
          <tr key={datum.label}>
            <th scope="row" className="py-2 text-left font-normal">
              {datum.label}
            </th>
            <td className="py-2 text-right tabular-nums">{valueFormatter(datum.value)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export type ChartContainerProps = ChartFrameProps;
export const ChartContainer = ChartFrame;

export type KPIWidgetProps = HTMLAttributes<HTMLElement> & {
  label: string;
  value: ReactNode;
  detail?: ReactNode;
};
export function KPIWidget({
  label,
  value,
  detail,
  className,
  ...props
}: KPIWidgetProps): React.JSX.Element {
  return (
    <article className={cn("bg-card rounded-lg border p-5", className)} {...props}>
      <p className="text-label text-muted-foreground">{label}</p>
      <p className="text-heading-1 mt-2 tabular-nums">{value}</p>
      {detail && <div className="text-small text-muted-foreground mt-1">{detail}</div>}
    </article>
  );
}

function toId(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}
