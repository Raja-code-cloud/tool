"use client";

import { Bell, ChevronLeft, ChevronRight, Menu } from "lucide-react";
import * as React from "react";

import { SearchField } from "@/components/forms/search-field";
import {
  Avatar,
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui";
import { useSidebar } from "@/hooks/use-sidebar";
import { cn } from "@/lib/utils/cn";

export type BreadcrumbItem = { label: string; href?: string };
export type BreadcrumbsProps = React.HTMLAttributes<HTMLElement> & {
  items: readonly BreadcrumbItem[];
};
export function Breadcrumbs({ items, className, ...props }: BreadcrumbsProps): React.JSX.Element {
  return (
    <nav aria-label="Breadcrumb" className={className} {...props}>
      <ol className="text-muted-foreground flex min-w-0 items-center gap-2 text-sm">
        {items.map((item, index) => (
          <li
            key={`${item.href ?? "current"}-${item.label}`}
            className={cn(
              "flex min-w-0 items-center gap-2",
              index > 0 && index < items.length - 1 && "max-sm:hidden",
            )}
          >
            {index > 0 && <span aria-hidden="true">/</span>}
            {item.href && index < items.length - 1 ? (
              <a
                className="hover:text-foreground focus-visible:ring-ring truncate focus-visible:ring-2 focus-visible:outline-none"
                href={item.href}
              >
                {item.label}
              </a>
            ) : (
              <span className="text-foreground truncate" aria-current="page">
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}

export type TabsItem = { id: string; label: string; disabled?: boolean };
export type TabsProps = React.HTMLAttributes<HTMLDivElement> & {
  items: readonly TabsItem[];
  value: string;
  onValueChange: (value: string) => void;
  label: string;
};
export function Tabs({
  items,
  value,
  onValueChange,
  label,
  className,
  ...props
}: TabsProps): React.JSX.Element {
  const refs = React.useRef<Array<HTMLButtonElement | null>>([]);
  const move = (from: number, delta: number): void => {
    const enabled = items
      .map((item, index) => ({ item, index }))
      .filter(({ item }) => !item.disabled);
    const current = enabled.findIndex(({ index }) => index === from);
    const next = enabled[(current + delta + enabled.length) % enabled.length];
    if (next) {
      onValueChange(next.item.id);
      refs.current[next.index]?.focus();
    }
  };
  const moveToEdge = (_from: number, edge: "start" | "end"): void => {
    const enabled = items
      .map((item, index) => ({ item, index }))
      .filter(({ item }) => !item.disabled);
    const target = edge === "start" ? enabled[0] : enabled[enabled.length - 1];
    if (target) {
      onValueChange(target.item.id);
      refs.current[target.index]?.focus();
    }
  };
  return (
    <div
      role="tablist"
      aria-label={label}
      className={cn("flex gap-1 overflow-x-auto border-b", className)}
      {...props}
    >
      {items.map((item, index) => (
        <button
          key={item.id}
          ref={(node) => {
            refs.current[index] = node;
          }}
          role="tab"
          id={`tab-${item.id}`}
          aria-selected={value === item.id}
          aria-controls={`panel-${item.id}`}
          tabIndex={value === item.id ? 0 : -1}
          disabled={item.disabled}
          onClick={() => onValueChange(item.id)}
          onKeyDown={(event) => {
            if (event.key === "ArrowRight") {
              event.preventDefault();
              move(index, 1);
            }
            if (event.key === "ArrowLeft") {
              event.preventDefault();
              move(index, -1);
            }
            if (event.key === "Home") {
              event.preventDefault();
              moveToEdge(index, "start");
            }
            if (event.key === "End") {
              event.preventDefault();
              moveToEdge(index, "end");
            }
          }}
          className="text-muted-foreground focus-visible:ring-ring aria-selected:border-primary aria-selected:text-foreground min-h-11 shrink-0 border-b-2 border-transparent px-3 text-sm font-semibold focus-visible:ring-2 focus-visible:outline-none disabled:opacity-50"
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}

export type PaginationProps = React.HTMLAttributes<HTMLElement> & {
  page: number;
  pageCount: number;
  pageSize?: number;
  total?: number;
  onPageChange: (page: number) => void;
};
export function Pagination({
  page,
  pageCount,
  pageSize,
  total,
  onPageChange,
  className,
  ...props
}: PaginationProps): React.JSX.Element {
  const start = total && pageSize ? Math.min((page - 1) * pageSize + 1, total) : undefined;
  const end = total && pageSize ? Math.min(page * pageSize, total) : undefined;
  return (
    <nav
      aria-label="Pagination"
      className={cn("flex flex-wrap items-center justify-between gap-3", className)}
      {...props}
    >
      <p className="text-muted-foreground text-sm tabular-nums">
        {start && end && total ? `${start}–${end} of ${total}` : `Page ${page} of ${pageCount}`}
      </p>
      <div className="flex gap-2">
        <Button
          variant="secondary"
          size="compact"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          <ChevronLeft className="size-4" /> Previous
        </Button>
        <Button
          variant="secondary"
          size="compact"
          disabled={page >= pageCount}
          onClick={() => onPageChange(page + 1)}
        >
          Next <ChevronRight className="size-4" />
        </Button>
      </div>
    </nav>
  );
}

export type SidebarItem = {
  label: string;
  href: string;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
};
export type SidebarProps = React.HTMLAttributes<HTMLElement> & {
  items: readonly SidebarItem[];
  currentHref?: string;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  linkComponent?: React.ElementType;
};
export function Sidebar({
  items,
  currentHref,
  header,
  footer,
  className,
  linkComponent,
  ...props
}: SidebarProps): React.JSX.Element {
  const { isOpen, isCollapsed, close } = useSidebar();

  // Escape dismisses the mobile drawer, matching standard overlay behaviour.
  React.useEffect(() => {
    if (!isOpen) return;
    const onKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape") close();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isOpen, close]);

  return (
    <>
      {isOpen && (
        <div
          className="bg-background/70 desktop:hidden motion-safe:animate-in motion-safe:fade-in fixed inset-0 z-30 backdrop-blur-xs"
          aria-hidden="true"
          onClick={close}
        />
      )}
      <aside
        className={cn(
          "w-sidebar bg-card desktop:sticky desktop:top-0 desktop:h-dvh desktop:translate-x-0 fixed inset-y-0 left-0 z-40 flex -translate-x-full flex-col border-r p-3 transition-[transform,width] duration-200 motion-reduce:transition-none",
          isOpen && "translate-x-0",
          isCollapsed && "desktop:w-sidebar-collapsed",
          className,
        )}
        {...props}
      >
        {header && <div className="mb-4">{header}</div>}
        <SidebarMenu
          items={items}
          {...(currentHref ? { currentHref } : {})}
          onNavigate={close}
          isCollapsed={isCollapsed}
          {...(linkComponent ? { linkComponent } : {})}
        />
        {footer && <div className="mt-4 border-t pt-4">{footer}</div>}
      </aside>
    </>
  );
}

export type NavItemProps = React.AnchorHTMLAttributes<HTMLAnchorElement> & {
  icon?: React.ReactNode;
  badge?: React.ReactNode;
  isActive?: boolean;
  isCollapsed?: boolean;
  as?: React.ElementType;
};
export function NavItem({
  icon,
  badge,
  isActive,
  isCollapsed,
  children,
  className,
  as: Component = "a",
  ...props
}: NavItemProps): React.JSX.Element {
  return (
    <Component
      aria-current={isActive ? "page" : undefined}
      title={isCollapsed && typeof children === "string" ? children : undefined}
      className={cn(
        "text-muted-foreground hover:bg-accent hover:text-foreground focus-visible:ring-ring aria-current:bg-accent aria-current:text-foreground aria-current:before:bg-primary relative flex min-h-11 items-center gap-2.5 rounded-md px-3 text-sm font-medium transition-[background-color,color,transform] duration-(--duration-fast) focus-visible:ring-2 active:scale-[0.99] aria-current:font-semibold aria-current:before:absolute aria-current:before:inset-y-2 aria-current:before:left-0 aria-current:before:w-0.5 aria-current:before:rounded-full motion-reduce:transition-none motion-reduce:active:scale-100 [&_svg]:size-4 [&_svg]:shrink-0",
        isCollapsed && "justify-center px-2",
        className,
      )}
      {...props}
    >
      {icon && <span aria-hidden="true">{icon}</span>}
      <span className={cn("flex-1", isCollapsed && "sr-only")}>{children}</span>
      {!isCollapsed && badge}
    </Component>
  );
}

export type SidebarMenuProps = {
  items: readonly SidebarItem[];
  currentHref?: string;
  onNavigate?: () => void;
  isCollapsed?: boolean;
  linkComponent?: React.ElementType;
};
export function SidebarMenu({
  items,
  currentHref,
  onNavigate,
  isCollapsed = false,
  linkComponent = "a",
}: SidebarMenuProps): React.JSX.Element {
  return (
    <nav aria-label="Primary" className="flex-1">
      <ul className="grid gap-1">
        {items.map((item) => (
          <li key={item.href}>
            <NavItem
              as={linkComponent}
              href={item.href}
              icon={item.icon}
              badge={item.badge}
              isActive={currentHref === item.href}
              isCollapsed={isCollapsed}
              onClick={onNavigate}
            >
              {item.label}
            </NavItem>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export type SidebarTriggerProps = React.ComponentProps<typeof Button>;
export function SidebarTrigger({ className, ...props }: SidebarTriggerProps): React.JSX.Element {
  const { isOpen, toggle } = useSidebar();
  return (
    <Button
      variant="icon"
      className={cn("desktop:hidden", className)}
      aria-label={isOpen ? "Close navigation" : "Open navigation"}
      aria-expanded={isOpen}
      onClick={toggle}
      {...props}
    >
      <Menu aria-hidden="true" />
    </Button>
  );
}

export const SearchBar = SearchField;
export type SearchBarProps = React.ComponentProps<typeof SearchField>;

export type NotificationButtonProps = Omit<React.ComponentProps<typeof Button>, "children"> & {
  count?: number;
};
export function NotificationButton({
  count = 0,
  ...props
}: NotificationButtonProps): React.JSX.Element {
  return (
    <Button
      variant="icon"
      aria-label={count > 0 ? `Notifications, ${count} unread` : "Notifications"}
      {...props}
    >
      <Bell aria-hidden="true" />
      {count > 0 && (
        <span
          className="bg-destructive absolute top-1 right-1 size-2 rounded-full"
          aria-hidden="true"
        />
      )}
    </Button>
  );
}

export type UserMenuProps = {
  name: string;
  email?: string;
  avatarUrl?: string;
  children: React.ReactNode;
};
export function UserMenu({ name, email, avatarUrl, children }: UserMenuProps): React.JSX.Element {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="min-h-11 px-2" aria-label={`Open menu for ${name}`}>
          <Avatar {...(avatarUrl ? { src: avatarUrl } : {})} alt={name} />
          <span className="tablet:block hidden text-left">
            <span className="block text-sm font-semibold">{name}</span>
            {email && <span className="text-muted-foreground block text-xs">{email}</span>}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">{children}</DropdownMenuContent>
    </DropdownMenu>
  );
}
