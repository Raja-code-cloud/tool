import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

export type ContainerProps = HTMLAttributes<HTMLDivElement> & { size?: "content" | "reading" };
export function Container({ size = "content", className, ...props }: ContainerProps): React.JSX.Element {
  return <div className={cn("page-gutter mx-auto w-full", size === "content" ? "max-w-content" : "max-w-reading", className)} {...props} />;
}

export type PageContainerProps = ContainerProps;
export function PageContainer(props: PageContainerProps): React.JSX.Element {
  return <Container {...props} />;
}

export type StackProps = HTMLAttributes<HTMLDivElement> & { gap?: "sm" | "md" | "lg" };
export function Stack({ gap = "md", className, ...props }: StackProps): React.JSX.Element {
  return <div className={cn("flex flex-col", gap === "sm" && "gap-3", gap === "md" && "gap-5", gap === "lg" && "gap-8", className)} {...props} />;
}

export type PageHeaderProps = HTMLAttributes<HTMLElement> & { title: string; description?: string; actions?: ReactNode; breadcrumbs?: ReactNode };
export function PageHeader({ title, description, actions, breadcrumbs, className, ...props }: PageHeaderProps): React.JSX.Element {
  return <header className={cn("grid gap-4", className)} {...props}>
    {breadcrumbs}
    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div className="min-w-0"><h1 className="text-heading-1">{title}</h1>{description && <p className="mt-1.5 max-w-reading text-body text-muted-foreground">{description}</p>}</div>
      {actions && <div className="flex shrink-0 flex-wrap gap-2">{actions}</div>}
    </div>
  </header>;
}

export type AppShellProps = HTMLAttributes<HTMLDivElement> & { sidebar?: ReactNode; header?: ReactNode; children: ReactNode };
export function AppShell({ sidebar, header, children, className, ...props }: AppShellProps): React.JSX.Element {
  return <div className={cn("min-h-dvh bg-background text-foreground desktop:grid desktop:grid-cols-[auto_1fr]", className)} {...props}>
    {sidebar}<div className="min-w-0">{header}<main id="main-content" tabIndex={-1} className="py-page-mobile outline-none tablet:py-page-tablet desktop:py-page-desktop">{children}</main></div>
  </div>;
}

export type SkipLinkProps = HTMLAttributes<HTMLAnchorElement> & { href?: string };
export function SkipLink({ href = "#main-content", className, children = "Skip to content", ...props }: SkipLinkProps): React.JSX.Element {
  return <a href={href} className={cn("sr-only z-100 rounded-md bg-primary px-4 py-2 text-primary-foreground focus:not-sr-only focus:fixed focus:top-2 focus:left-2", className)} {...props}>{children}</a>;
}

export type AppHeaderProps = HTMLAttributes<HTMLElement> & { leading?: ReactNode; search?: ReactNode; actions?: ReactNode; title?: string };
export function AppHeader({ leading, search, actions, title, className, ...props }: AppHeaderProps): React.JSX.Element {
  return <header className={cn("page-gutter sticky top-0 z-20 flex min-h-header items-center gap-3 border-b bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/70", className)} {...props}>{leading}{title && <p className="min-w-0 flex-1 truncate text-heading-3 tablet:hidden">{title}</p>}{search && <div className="hidden min-w-0 max-w-xl flex-1 tablet:block">{search}</div>}{actions && <div className="ml-auto flex shrink-0 items-center gap-1">{actions}</div>}</header>;
}

export type TopNavbarProps = AppHeaderProps;
export function TopNavbar(props: TopNavbarProps): React.JSX.Element {
  return <AppHeader {...props} />;
}

export const Navbar = TopNavbar;
