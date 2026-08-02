import type { ReactNode } from "react";

import { Card, CardHeader } from "@/components/cards";
import { cn } from "@/lib/utils/cn";

export type SettingsSectionProps = {
  id: string;
  title: string;
  description: string;
  action?: ReactNode;
  footer?: ReactNode;
  isDestructive?: boolean;
  children: ReactNode;
};

/**
 * Settings card shell. `scroll-mt` keeps the heading clear of the sticky
 * application header when the in-page nav jumps to an anchor.
 */
export function SettingsSection({ id, title, description, action, footer, isDestructive = false, children }: SettingsSectionProps): React.JSX.Element {
  return (
    <Card
      as="section"
      id={id}
      aria-label={title}
      className={cn("scroll-mt-20 p-0", isDestructive && "border-destructive/50")}
    >
      <div className="p-5">
        <CardHeader title={title} description={description} action={action} headingLevel={2} className="mb-5" />
        {children}
      </div>
      {footer && <div className="flex flex-wrap items-center justify-end gap-2 border-t bg-muted/30 px-5 py-3">{footer}</div>}
    </Card>
  );
}

export type SettingRowProps = {
  label: string;
  description?: string;
  htmlFor?: string;
  control: ReactNode;
  isStacked?: boolean;
};

/** Label/description on the leading edge, control on the trailing edge. */
export function SettingRow({ label, description, htmlFor, control, isStacked = false }: SettingRowProps): React.JSX.Element {
  return (
    <div className={cn("flex gap-4 py-3.5", isStacked ? "flex-col" : "flex-col tablet:flex-row tablet:items-center tablet:justify-between")}>
      <div className="min-w-0">
        {htmlFor ? (
          <label htmlFor={htmlFor} className="text-sm font-semibold">{label}</label>
        ) : (
          <p className="text-sm font-semibold">{label}</p>
        )}
        {description && <p className="mt-1 max-w-prose text-sm text-muted-foreground">{description}</p>}
      </div>
      <div className={cn("shrink-0", !isStacked && "tablet:w-64")}>{control}</div>
    </div>
  );
}

/** Divided list of setting rows. */
export function SettingRows({ children }: { children: ReactNode }): React.JSX.Element {
  return <div className="divide-y">{children}</div>;
}
