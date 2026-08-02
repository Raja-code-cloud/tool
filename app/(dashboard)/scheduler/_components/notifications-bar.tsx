"use client";

import { Alert } from "@/components/feedback";
import type { SchedulerNotification } from "@/lib/domain/scheduler";

export function NotificationsBar({
  notifications,
}: {
  notifications: readonly SchedulerNotification[];
}): React.JSX.Element | null {
  if (notifications.length === 0) return null;

  const latest = notifications.slice(0, 2);

  return (
    <div className="grid gap-2" role="region" aria-label="Scheduler notifications">
      {latest.map((notification) => (
        <Alert
          key={notification.id}
          variant={
            notification.variant === "success"
              ? "success"
              : notification.variant === "warning"
                ? "warning"
                : "info"
          }
          title="Notification"
        >
          {notification.message}
        </Alert>
      ))}
    </div>
  );
}
