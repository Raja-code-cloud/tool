import { AlertTriangle, CalendarClock, CheckCircle2, FileStack, FileText } from "lucide-react";
import type { DashboardStatData } from "@/lib/domain/dashboard";
import { cn } from "@/lib/utils/cn";

type DashboardStatsProps = {
  readonly stats: readonly DashboardStatData[];
};

export function DashboardStats({ stats }: DashboardStatsProps): React.JSX.Element {
  return (
    <section aria-labelledby="dashboard-stats-heading">
      <h2 id="dashboard-stats-heading" className="sr-only">
        Key metrics
      </h2>
      <div className="tablet:grid-cols-2 wide:grid-cols-5 grid gap-4">
        {stats.map((stat) => {
          const Icon = DASHBOARD_STAT_ICONS[stat.id] ?? FileStack;
          const TrendIcon = stat.trendDirection === "down" ? TrendingDown : TrendingUp;

          return (
            <MetricCard
              key={stat.id}
              label={stat.label}
              value={stat.value}
              comparison={stat.comparison}
              trend={
                stat.trendDirection !== "neutral" ? (
                  <span
                    className={cn(
                      "inline-flex items-center gap-0.5 font-semibold",
                      stat.trendDirection === "up" ? "text-success" : "text-destructive",
                    )}
                  >
                    <TrendIcon className="size-3.5" aria-hidden="true" />
                    {stat.trend}
                  </span>
                ) : (
                  <span
                    className={cn(
                      "font-semibold",
                      stat.variant === "warning" ? "text-warning" : "text-muted-foreground",
                    )}
                  >
                    {stat.trend}
                  </span>
                )
              }
              visualization={
                <span
                  aria-hidden="true"
                  className={cn(
                    "grid size-10 place-items-center rounded-lg",
                    stat.variant === "warning"
                      ? "bg-warning/15 text-warning"
                      : "bg-primary/15 text-primary",
                  )}
                >
                  <Icon className="size-5" />
                </span>
              }
            />
          );
        })}
      </div>
    </section>
  );
}
