import Link from "next/link";

import { AgendaList } from "@/components/calendar";
import { Card, CardHeader } from "@/components/cards";
import { StatusBadge } from "@/components/feedback";
import { Button } from "@/components/ui";
import { ROUTES } from "@/constants/navigation";
import type { AgendaEntry } from "@/lib/domain/dashboard";

const STATUS_CHIP = {
  queued: { variant: "info" as const, label: "Queued" },
  published: { variant: "success" as const, label: "Published" },
  failed: { variant: "danger" as const, label: "Failed" },
};

type PublishingCalendarPanelProps = {
  readonly agenda: readonly AgendaEntry[];
};

export function PublishingCalendarPanel({ agenda }: PublishingCalendarPanelProps): React.JSX.Element {
  const items = agenda.map((entry) => ({
    id: entry.id,
    time: entry.time,
    title: entry.title,
    meta: entry.platform,
    status: (
      <StatusBadge variant={STATUS_CHIP[entry.status].variant}>
        {STATUS_CHIP[entry.status].label}
      </StatusBadge>
    ),
  }));

  return (
    <Card as="section" aria-labelledby="publishing-calendar-heading" className="h-full">
      <CardHeader
        title="Publishing calendar"
        description="Today's queue across connected channels."
        headingLevel={2}
        headingId="publishing-calendar-heading"
        action={
          <Button asChild variant="ghost" size="compact">
            <Link href={ROUTES.calendar}>View calendar</Link>
          </Button>
        }
      />
      <AgendaList dateLabel="Today" items={items} empty="Nothing scheduled for today." />
    </Card>
  );
}
