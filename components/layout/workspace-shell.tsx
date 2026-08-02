"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { CloudLightning, LogOut, PanelLeftClose, PanelLeftOpen, Plus, Settings, UserRound } from "lucide-react";

import { AppHeader, AppShell } from "@/components/layout/layout";
import { PageTransition } from "@/components/layout/page-transition";
import { Breadcrumbs, NotificationButton, SearchBar, Sidebar, SidebarTrigger, UserMenu } from "@/components/navigation";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { Button, DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui";
import { useSidebar } from "@/hooks/use-sidebar";
import { CURRENT_USER, UNREAD_NOTIFICATION_COUNT, WORKSPACE } from "@/constants/workspace";
import { NAV_ROUTES, ROUTES } from "@/constants/navigation";
import { buildBreadcrumbs, isRouteActive } from "@/lib/utils/navigation";

const QUICK_ACTIONS = [
  { label: "Upload content", href: ROUTES.upload },
  { label: "Generate with AI", href: ROUTES.aiStudio },
  { label: "Schedule a post", href: ROUTES.scheduler },
] as const;

function WorkspaceBrand({ isCollapsed }: { isCollapsed: boolean }): React.JSX.Element {
  return (
    <Link href={ROUTES.dashboard} className="flex min-h-11 items-center gap-2 rounded-md px-2 focus-visible:ring-2 focus-visible:ring-ring">
      <span aria-hidden="true" className="grid size-8 shrink-0 place-items-center rounded-lg bg-primary text-primary-foreground">
        <CloudLightning className="size-4" />
      </span>
      <span className={isCollapsed ? "sr-only" : "min-w-0 truncate font-semibold"}>{WORKSPACE.name}</span>
    </Link>
  );
}

function CollapseToggle(): React.JSX.Element {
  const { isCollapsed, toggleCollapsed } = useSidebar();
  return (
    <Button
      variant="ghost"
      size="compact"
      className="hidden w-full justify-start desktop:flex"
      aria-expanded={!isCollapsed}
      aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      onClick={toggleCollapsed}
    >
      {isCollapsed ? <PanelLeftOpen className="size-4" aria-hidden="true" /> : <PanelLeftClose className="size-4" aria-hidden="true" />}
      <span className={isCollapsed ? "sr-only" : undefined}>Collapse</span>
    </Button>
  );
}

function QuickActionsMenu(): React.JSX.Element {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button size="compact" className="max-sm:px-2">
          <Plus className="size-4" aria-hidden="true" />
          <span className="max-sm:sr-only">Create</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel className="px-3 py-2 text-xs font-semibold text-muted-foreground">Quick actions</DropdownMenuLabel>
        {QUICK_ACTIONS.map((action) => (
          <DropdownMenuItem key={action.href} asChild>
            <Link href={action.href}>{action.label}</Link>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export type WorkspaceShellProps = { children: React.ReactNode };

/**
 * Application frame shared by every workspace route: sidebar, sticky header,
 * and the main content region. Composed exclusively from the existing
 * component library so feature pages never build their own chrome.
 */
export function WorkspaceShell({ children }: WorkspaceShellProps): React.JSX.Element {
  const pathname = usePathname();
  const { isCollapsed } = useSidebar();

  const items = React.useMemo(
    () => NAV_ROUTES.map(({ label, href, icon: Icon }) => ({ label, href, icon: <Icon className="size-4" /> })),
    [],
  );
  const crumbs = React.useMemo(() => buildBreadcrumbs(pathname), [pathname]);
  const activeHref = NAV_ROUTES.find((route) => isRouteActive(pathname, route.href))?.href;
  const activeLabel = crumbs.at(-1)?.label ?? WORKSPACE.shortName;

  return (
    <AppShell
      sidebar={
        <Sidebar
          items={items}
          {...(activeHref ? { currentHref: activeHref } : {})}
          linkComponent={Link}
          header={<WorkspaceBrand isCollapsed={isCollapsed} />}
          footer={<CollapseToggle />}
        />
      }
      header={
        <AppHeader
          title={activeLabel}
          leading={
            <div className="flex min-w-0 items-center gap-2">
              <SidebarTrigger />
              <Breadcrumbs items={crumbs} className="hidden min-w-0 tablet:block" />
            </div>
          }
          search={<SearchBar placeholder="Search content, campaigns, assets" aria-keyshortcuts="Control+K Meta+K" />}
          actions={
            <>
              <QuickActionsMenu />
              <NotificationButton className="relative" count={UNREAD_NOTIFICATION_COUNT} />
              <ThemeToggle />
              <UserMenu name={CURRENT_USER.name} email={CURRENT_USER.email}>
                <DropdownMenuLabel className="px-3 py-2 text-xs font-semibold text-muted-foreground">{CURRENT_USER.role}</DropdownMenuLabel>
                <DropdownMenuItem asChild>
                  <Link href={ROUTES.settings}><UserRound className="size-4" aria-hidden="true" />Profile</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href={ROUTES.settings}><Settings className="size-4" aria-hidden="true" />Settings</Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator className="my-1 h-px bg-border" />
                <DropdownMenuItem isDestructive>
                  <LogOut className="size-4" aria-hidden="true" />Sign out
                </DropdownMenuItem>
              </UserMenu>
            </>
          }
        />
      }
    >
      <PageTransition>{children}</PageTransition>
    </AppShell>
  );
}
