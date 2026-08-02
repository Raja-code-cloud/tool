"use client";

import { AlertTriangle, CheckCircle2, Clock, Link2, Link2Off } from "lucide-react";

import { MetricCard } from "@/components/cards";
import { formatNumber } from "@/lib/utils/formatting";
import type { SocialAccountsOverview } from "@/lib/utils/social-accounts";

export function OverviewCards({
  overview,
}: {
  overview: SocialAccountsOverview;
}): React.JSX.Element {
  const cards = [
    { label: "Connected accounts", value: overview.connected, icon: Link2 },
    { label: "Disconnected accounts", value: overview.disconnected, icon: Link2Off },
    { label: "Publishing enabled", value: overview.publishingEnabled, icon: CheckCircle2 },
    {
      label: "Publishing errors",
      value: overview.publishingErrors,
      icon: AlertTriangle,
      variant: overview.publishingErrors > 0 ? ("warning" as const) : undefined,
    },
    {
      label: "Upcoming token expiry",
      value: overview.tokenExpiring,
      icon: Clock,
      variant: overview.tokenExpiring > 0 ? ("warning" as const) : undefined,
    },
  ];

  return (
    <section aria-labelledby="overview-heading">
      <h2 id="overview-heading" className="sr-only">
        Account overview
      </h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <MetricCard
              key={card.label}
              label={card.label}
              value={formatNumber(card.value)}
              visualization={
                <span
                  aria-hidden="true"
                  className={`grid size-10 place-items-center rounded-lg ${card.variant === "warning" ? "bg-warning/15 text-warning" : "bg-primary/15 text-primary"}`}
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
