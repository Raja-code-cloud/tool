"use client";

import { Alert } from "@/components/feedback";
import type { ScheduleConflict } from "@/lib/utils/scheduler";

export function ConflictAlerts({
  conflicts,
}: {
  conflicts: readonly ScheduleConflict[];
}): React.JSX.Element | null {
  if (conflicts.length === 0) return null;

  const visible = conflicts.slice(0, 3);

  return (
    <div className="grid gap-2" role="region" aria-label="Schedule conflicts">
      {visible.map((conflict) => (
        <Alert
          key={conflict.id}
          variant={
            conflict.type === "missing_content" || conflict.type === "past_schedule"
              ? "warning"
              : "danger"
          }
          title="Publishing conflict"
        >
          {conflict.message}
        </Alert>
      ))}
      {conflicts.length > 3 && (
        <p className="text-muted-foreground text-xs">
          +{conflicts.length - 3} more conflicts detected
        </p>
      )}
    </div>
  );
}
