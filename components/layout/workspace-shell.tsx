"use client";

import { MotionConfig } from "framer-motion";
import {
  CloudLightning,
  LogOut,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  Settings,
  UserRound,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import * as React from "react";

import { AppHeader, AppShell } from "@/components/layout/layout";
import { PageTransition } from "@/components/layout/page-transition";
import {
  Breadcrumbs,
  NotificationButton,
  SearchBar,
  Sidebar,
  SidebarTrigger,
  UserMenu,
} from "@/components/navigation";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui";
import { NAV_ROUTES, ROUTES } from "@/constants/navigation";
import { useAuth } from "@/hooks/use-auth";
import { useSidebar } from "@/hooks/use-sidebar";
import type { WorkspaceInfo } from "@/lib/domain/workspace";
import { purgeExpiredClientStorage } from "@/lib/security";
import { workspaceService } from "@/lib/services";
import { buildBreadcrumbs, isRouteActive } from "@/lib/utils/navigation";

const FALLBACK_WORKSPACE: WorkspaceInfo = {
  name: "Workspace",
  shortName: "WS",
  description: "",
};

const QUICK_ACTIONS = [
  { label: "Upload content", href: ROUTES.upload },
  { label: "Generate with AI", href: ROUTES.aiStudio },
  { label: "Schedule a post", href: ROUTES.scheduler },
] as const;

function WorkspaceBrand({
  isCollapsed,
  workspace,
}: {
  isCollapsed: boolean;
  workspace: WorkspaceInfo;
}): React.JSX.Element {
  return (
    <Link
      href={ROUTES.dashboard}
      className="focus-visible:ring-ring flex min-h-11 items-center gap-2 rounded-md px-2 focus-visible:ring-2"
    >
      <span
        aria-hidden="true"
        className="bg-primary text-primary-foreground grid size-8 shrink-0 place-items-center rounded-lg"
      >
        <CloudLightning className="size-4" />
      </span>
      <span className={isCollapsed ? "sr-only" : "min-w-0 truncate font-semibold"}>
        {workspace.name}
      </span>
    </Link>
  );
}

function CollapseToggle(): React.JSX.Element {
  const { isCollapsed, toggleCollapsed } = useSidebar();
  return (
    <Button
      variant="ghost"
      size="compact"
      className="desktop:flex hidden w-full justify-start"
      aria-expanded={!isCollapsed}
      aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      onClick={toggleCollapsed}
    >
      {isCollapsed ? (
        <PanelLeftOpen className="size-4" aria-hidden="true" />
      ) : (
        <PanelLeftClose className="size-4" aria-hidden="true" />
      )}
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
        <DropdownMenuLabel className="text-muted-foreground px-3 py-2 text-xs font-semibold">
          Quick actions
        </DropdownMenuLabel>
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
  const { user, signOut } = useAuth();
  const [workspace, setWorkspace] = React.useState<WorkspaceInfo>(FALLBACK_WORKSPACE);
  const [unreadNotificationCount, setUnreadNotificationCount] = React.useState(0);

  const currentUser = user ?? { name: "Member", email: "", role: "Member" };

  React.useEffect(() => {
    purgeExpiredClientStorage();
  }, []);

  React.useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const [loadedWorkspace, unreadCount] = await Promise.all([
          workspaceService.getWorkspace(),
          workspaceService.getUnreadNotificationCount(),
        ]);
        if (!cancelled) {
          setWorkspace(loadedWorkspace);
          setUnreadNotificationCount(unreadCount);
        }
      } catch {
        if (!cancelled) {
          setWorkspace(FALLBACK_WORKSPACE);
          setUnreadNotificationCount(0);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSignOut = React.useCallback(() => {
    void signOut();
  }, [signOut]);

  const items = React.useMemo(
    () =>
      NAV_ROUTES.map(({ label, href, icon: Icon }) => ({
        label,
        href,
        icon: <Icon className="size-4" />,
      })),
    [],
  );
  const crumbs = React.useMemo(() => buildBreadcrumbs(pathname), [pathname]);
  const activeHref = NAV_ROUTES.find((route) => isRouteActive(pathname, route.href))?.href;
  const activeLabel = crumbs.at(-1)?.label ?? workspace.shortName;

  return (
    <MotionConfig reducedMotion="user">
      <AppShell
        sidebar={
          <Sidebar
            items={items}
            {...(activeHref ? { currentHref: activeHref } : {})}
            linkComponent={Link}
            header={<WorkspaceBrand isCollapsed={isCollapsed} workspace={workspace} />}
            footer={<CollapseToggle />}
          />
        }
        header={
          <AppHeader
            title={activeLabel}
            leading={
              <div className="flex min-w-0 items-center gap-2">
                <SidebarTrigger />
                <Breadcrumbs items={crumbs} className="tablet:block hidden min-w-0" />
              </div>
            }
            search={
              <SearchBar
                placeholder="Search content, campaigns, assets"
                aria-keyshortcuts="Control+K Meta+K"
              />
            }
            actions={
              <>
                <QuickActionsMenu />
                <NotificationButton className="relative" count={unreadNotificationCount} />
                <ThemeToggle />
                <UserMenu name={currentUser.name} email={currentUser.email}>
                  <DropdownMenuLabel className="text-muted-foreground px-3 py-2 text-xs font-semibold">
                    {currentUser.role}
                  </DropdownMenuLabel>
                  <DropdownMenuItem asChild>
                    <Link href={ROUTES.settings}>
                      <UserRound className="size-4" aria-hidden="true" />
                      Profile
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href={ROUTES.settings}>
                      <Settings className="size-4" aria-hidden="true" />
                      Settings
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="bg-border my-1 h-px" />
                  <DropdownMenuItem isDestructive onSelect={handleSignOut}>
                    <LogOut className="size-4" aria-hidden="true" />
                    Sign out
                  </DropdownMenuItem>
                </UserMenu>
              </>
            }
          />
        }
      >
        <PageTransition>{children}</PageTransition>
      </AppShell>
    </MotionConfig>
  );
}
