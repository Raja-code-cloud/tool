import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "../../lib/utils/cn";

export type CardProps = HTMLAttributes<HTMLElement> & { as?: "article" | "section" | "div" };
export function Card({ as: Component = "div", className, ...props }: CardProps): React.JSX.Element {
  return (
    <Component
      className={cn("bg-card text-card-foreground rounded-xl border p-5", className)}
      {...props}
    />
  );
}

export type CardHeaderProps = HTMLAttributes<HTMLDivElement> & {
  title: string;
  description?: string;
  action?: ReactNode;
  headingLevel?: 2 | 3 | 4;
  /** Stable id for the heading element; use with section `aria-labelledby`. */
  headingId?: string;
};
export function CardHeader({
  title,
  description,
  action,
  headingLevel = 3,
  headingId,
  className,
  ...props
}: CardHeaderProps): React.JSX.Element {
  const Heading = `h${headingLevel}` as const;
  return (
    <div
      className={cn(
        "tablet:flex-row tablet:items-start tablet:justify-between tablet:gap-4 mb-4 flex flex-col gap-3",
        className,
      )}
      {...props}
    >
      <div className="min-w-0">
        <Heading {...(headingId ? { id: headingId } : {})} className="text-heading-3">
          {title}
        </Heading>
        {description && (
          <p className="max-w-reading text-body text-muted-foreground mt-1">{description}</p>
        )}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}

export type MetricCardProps = HTMLAttributes<HTMLElement> & {
  label: string;
  value: ReactNode;
  trend?: ReactNode;
  comparison?: string;
  visualization?: ReactNode;
};
export function MetricCard({
  label,
  value,
  trend,
  comparison,
  visualization,
  className,
  ...props
}: MetricCardProps): React.JSX.Element {
  return (
    <Card as="article" className={cn("hover-raise", className)} {...props}>
      <p className="text-eyebrow">{label}</p>
      <div className="mt-2 flex items-end justify-between gap-4">
        <div>
          <p className="text-display tabular-nums">{value}</p>
          {(trend || comparison) && (
            <p className="text-small text-muted-foreground mt-1 flex items-center gap-1">
              {trend}
              {comparison}
            </p>
          )}
        </div>
        {visualization}
      </div>
    </Card>
  );
}

export type InteractiveCardProps = CardProps & { href: string; title: string };
export function InteractiveCard({
  href,
  title,
  children,
  className,
  ...props
}: InteractiveCardProps): React.JSX.Element {
  return (
    <Card
      as="article"
      className={cn(
        "hover-raise hover:border-primary/40 hover:bg-accent/30 focus-within:ring-ring relative focus-within:ring-2",
        className,
      )}
      {...props}
    >
      <h3 className="text-heading-3">
        <a href={href} className="after:absolute after:inset-0 focus-visible:outline-none">
          {title}
        </a>
      </h3>
      <div className="text-body text-muted-foreground relative mt-2">{children}</div>
    </Card>
  );
}

export type ContentCardProps = CardProps;
export const ContentCard = Card;

export type StatCardProps = MetricCardProps;
export const StatCard = MetricCard;

export type AnalyticsCardProps = MetricCardProps;
export const AnalyticsCard = MetricCard;

export type UploadCardProps = CardProps;
export function UploadCard({ className, ...props }: UploadCardProps): React.JSX.Element {
  return <Card className={cn("border-dashed", className)} {...props} />;
}
