import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "../../lib/utils/cn";
import { Avatar } from "../ui";

export type AvatarGroupItem = { id: string; name: string; src?: string };
export type AvatarGroupProps = HTMLAttributes<HTMLDivElement> & {
  items: readonly AvatarGroupItem[];
  maximum?: number;
};
export function AvatarGroup({
  items,
  maximum = 3,
  className,
  ...props
}: AvatarGroupProps): React.JSX.Element {
  const visible = items.slice(0, maximum);
  const remainder = Math.max(0, items.length - visible.length);
  return (
    <div
      className={cn("flex -space-x-2", className)}
      aria-label={items.map(({ name }) => name).join(", ")}
      {...props}
    >
      {visible.map((item) => (
        <Avatar
          key={item.id}
          {...(item.src ? { src: item.src } : {})}
          alt={item.name}
          size="sm"
          className="ring-card ring-2"
        />
      ))}
      {remainder > 0 && (
        <span
          className="bg-muted ring-card grid size-6 place-items-center rounded-full text-xs font-semibold ring-2"
          aria-label={`${remainder} more`}
        >
          +{remainder}
        </span>
      )}
    </div>
  );
}

export type ToolbarProps = HTMLAttributes<HTMLDivElement> & { label: string };
export function Toolbar({ label, className, ...props }: ToolbarProps): React.JSX.Element {
  return (
    <div
      role="toolbar"
      aria-label={label}
      className={cn("flex min-h-11 flex-wrap items-center gap-2", className)}
      {...props}
    />
  );
}

export type KeyValueListItem = { id: string; term: ReactNode; description: ReactNode };
export type KeyValueListProps = HTMLAttributes<HTMLDListElement> & {
  items: readonly KeyValueListItem[];
};
export function KeyValueList({ items, className, ...props }: KeyValueListProps): React.JSX.Element {
  return (
    <dl className={cn("grid gap-3 text-sm", className)} {...props}>
      {items.map((item) => (
        <div key={item.id} className="grid grid-cols-[minmax(7rem,1fr)_2fr] gap-4">
          <dt className="text-muted-foreground">{item.term}</dt>
          <dd className="min-w-0 font-medium">{item.description}</dd>
        </div>
      ))}
    </dl>
  );
}

export type VisuallyHiddenProps = HTMLAttributes<HTMLSpanElement>;
export function VisuallyHidden({ className, ...props }: VisuallyHiddenProps): React.JSX.Element {
  return <span className={cn("sr-only", className)} {...props} />;
}
