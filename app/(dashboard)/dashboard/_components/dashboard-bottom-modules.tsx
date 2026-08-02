import Link from "next/link";

import { Card, CardHeader } from "@/components/cards";
import { Progress, StatusBadge } from "@/components/feedback";
import { Button } from "@/components/ui";
import { ROUTES } from "@/constants/navigation";
import type { ActivityItem, DashboardStorage, PlatformHealth } from "@/lib/domain/dashboard";
import { formatBytes, formatDate, formatPercent } from "@/lib/utils/formatting";

const PLATFORM_STATUS = {
  healthy: "success",
  warning: "warning",
  error: "danger",
} as const;

type DashboardBottomModulesProps = {
  readonly recentActivity: readonly ActivityItem[];
  readonly platformHealth: readonly PlatformHealth[];
  readonly storage: DashboardStorage;
};

export function DashboardBottomModules({
  recentActivity,
  platformHealth,
  storage,
}: DashboardBottomModulesProps): React.JSX.Element {
  const usedRatio = storage.totalBytes > 0 ? storage.usedBytes / storage.totalBytes : 0;

  return (
    <section aria-labelledby="dashboard-modules-heading" className="wide:grid-cols-3 grid gap-4">
      <h2 id="dashboard-modules-heading" className="sr-only">
        Workspace modules
      </h2>

      <Card as="section" aria-labelledby="recent-activity-heading">
        <CardHeader
          title="Recent activity"
          description="Latest events across the workspace."
          headingLevel={3}
          headingId="recent-activity-heading"
        />
        {recentActivity.length === 0 ? (
          <p className="text-muted-foreground text-sm">No recent activity yet.</p>
        ) : (
          <ul className="divide-y">
            {recentActivity.map((item) => (
              <li key={item.id} className="py-3 first:pt-0 last:pb-0">
                <p className="text-sm">
                  <span className="font-semibold">{item.actor}</span>{" "}
                  <span className="text-muted-foreground">{item.action}</span>{" "}
                  <span className="font-medium">{item.target}</span>
                </p>
                <time
                  dateTime={item.occurredAt}
                  className="text-small text-muted-foreground mt-1 block"
                >
                  {formatDate(item.occurredAt, { dateStyle: "medium", timeStyle: "short" })}
                </time>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card as="section" aria-labelledby="platform-health-heading">
        <CardHeader
          title="Platform health"
          description="Connection and publishing status."
          headingLevel={3}
          headingId="platform-health-heading"
          action={
            <Button asChild variant="ghost" size="compact">
              <Link href={ROUTES.socialAccounts}>Manage</Link>
            </Button>
          }
        />
        {platformHealth.length === 0 ? (
          <p className="text-muted-foreground text-sm">Platform health data is unavailable.</p>
        ) : (
          <ul className="grid gap-2">
            {platformHealth.map((platform) => (
              <li
                key={platform.id}
                className="flex items-center justify-between gap-3 rounded-lg border px-3 py-2.5"
              >
                <div className="min-w-0">
                  <p className="text-sm font-semibold">{platform.name}</p>
                  <p className="text-small text-muted-foreground">{platform.detail}</p>
                </div>
                <StatusBadge variant={PLATFORM_STATUS[platform.status]}>
                  {platform.status === "healthy"
                    ? "Healthy"
                    : platform.status === "warning"
                      ? "Warning"
                      : "Error"}
                </StatusBadge>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card as="section" aria-labelledby="storage-usage-heading">
        <CardHeader
          title="Storage usage"
          description={storage.label}
          headingLevel={3}
          headingId="storage-usage-heading"
        />
        <Progress value={Math.round(usedRatio * 100)} label="Storage used" />
        <p className="text-muted-foreground mt-2 text-sm">
          {formatBytes(storage.usedBytes)} of {formatBytes(storage.totalBytes)} (
          {formatPercent(usedRatio)})
        </p>
        <Button asChild variant="secondary" size="compact" className="mt-4">
          <Link href={ROUTES.settings}>Storage settings</Link>
        </Button>
      </Card>
    </section>
  );
}
