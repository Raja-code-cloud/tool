import type { ReactNode } from "react";

import { ThemeProvider, type Theme } from "@/components/theme/theme-provider";
import { AuthProvider } from "@/hooks/use-auth";
import { SidebarProvider } from "@/hooks/use-sidebar";
import { AppToastProvider } from "@/hooks/use-toast";

export type TestProvidersProps = {
  children: ReactNode;
  theme?: Theme;
  withSidebar?: boolean;
  sidebarCollapsed?: boolean;
};

export function TestProviders({
  children,
  theme = "dark",
  withSidebar = false,
  sidebarCollapsed = false,
}: TestProvidersProps): React.JSX.Element {
  const content = withSidebar ? (
    <SidebarProvider defaultCollapsed={sidebarCollapsed}>{children}</SidebarProvider>
  ) : (
    children
  );

  return (
    <ThemeProvider defaultTheme={theme} storageKey="test-theme">
      <AppToastProvider>
        <AuthProvider>{content}</AuthProvider>
      </AppToastProvider>
    </ThemeProvider>
  );
}
