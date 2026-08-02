import {
  BarChart3,
  CalendarDays,
  Clock4,
  LayoutDashboard,
  Library,
  Settings,
  Share2,
  Sparkles,
  Upload,
  type LucideIcon,
} from "lucide-react";

export const ROUTES = {
  dashboard: "/dashboard",
  contentLibrary: "/content-library",
  upload: "/upload",
  aiStudio: "/ai-studio",
  scheduler: "/scheduler",
  calendar: "/calendar",
  analytics: "/analytics",
  socialAccounts: "/social-accounts",
  settings: "/settings",
} as const;

export type NavRoute = {
  readonly label: string;
  readonly href: string;
  readonly icon: LucideIcon;
  readonly description: string;
};

export const NAV_ROUTES: readonly NavRoute[] = [
  {
    label: "Dashboard",
    href: ROUTES.dashboard,
    icon: LayoutDashboard,
    description: "Performance overview across every connected channel.",
  },
  {
    label: "Content Library",
    href: ROUTES.contentLibrary,
    icon: Library,
    description: "Every asset, draft, and published post in one place.",
  },
  {
    label: "Upload Wizard",
    href: ROUTES.upload,
    icon: Upload,
    description: "Guided multi-step upload and enrichment flow.",
  },
  {
    label: "AI Studio",
    href: ROUTES.aiStudio,
    icon: Sparkles,
    description: "Generate captions, variants, and creative briefs.",
  },
  {
    label: "Scheduler",
    href: ROUTES.scheduler,
    icon: Clock4,
    description: "Queue and automate publishing windows.",
  },
  {
    label: "Calendar",
    href: ROUTES.calendar,
    icon: CalendarDays,
    description: "Monthly and weekly editorial calendar.",
  },
  {
    label: "Analytics",
    href: ROUTES.analytics,
    icon: BarChart3,
    description: "Engagement, reach, and conversion reporting.",
  },
  {
    label: "Social Accounts",
    href: ROUTES.socialAccounts,
    icon: Share2,
    description: "Connect and manage publishing destinations.",
  },
  {
    label: "Settings",
    href: ROUTES.settings,
    icon: Settings,
    description: "Workspace, billing, and member preferences.",
  },
];

export function findRouteByHref(href: string): NavRoute | undefined {
  return NAV_ROUTES.find((route) => route.href === href);
}
