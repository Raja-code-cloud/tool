import type { Metadata } from "next";

import { findRouteByHref, ROUTES } from "@/constants/navigation";

export type Crumb = { label: string; href?: string };

function humanizeSegment(segment: string): string {
  return segment
    .split("-")
    .filter(Boolean)
    .map((word) => `${word.charAt(0).toUpperCase()}${word.slice(1)}`)
    .join(" ");
}

/**
 * Derives breadcrumb entries from a pathname. Labels resolve from the
 * navigation constants so a crumb always matches its sidebar wording, and
 * fall back to a humanized slug for nested routes.
 */
export function buildBreadcrumbs(pathname: string): Crumb[] {
  const segments = pathname.split("/").filter(Boolean);
  if (segments.length === 0) return [{ label: "Home" }];

  const crumbs = segments.map((segment, index) => {
    const href = `/${segments.slice(0, index + 1).join("/")}`;
    const label = findRouteByHref(href)?.label ?? humanizeSegment(segment);
    return { label, href };
  });

  // The dashboard is the workspace root, so it never needs a "Home" ancestor.
  if (crumbs[0]?.href === ROUTES.dashboard) return crumbs;

  return [{ label: "Home", href: ROUTES.dashboard }, ...crumbs];
}

/**
 * Page metadata derived from the navigation constants, so a route's title and
 * description are defined exactly once and always match the sidebar.
 */
export function buildRouteMetadata(href: string): Metadata {
  const route = findRouteByHref(href);
  if (!route) return {};
  return { title: route.label, description: route.description };
}

/** True when `href` is the active route or an ancestor of it. */
export function isRouteActive(pathname: string, href: string): boolean {
  return pathname === href || pathname.startsWith(`${href}/`);
}
