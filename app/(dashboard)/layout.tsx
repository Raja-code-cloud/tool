import { WorkspaceShell } from "@/components/layout";
import { SidebarProvider } from "@/hooks/use-sidebar";

/**
 * Every workspace route renders inside the shared shell, so no feature page
 * composes its own sidebar, header, or content frame.
 */
export default function DashboardLayout({
  children,
}: Readonly<{ children: React.ReactNode }>): React.JSX.Element {
  return (
    <SidebarProvider>
      <WorkspaceShell>{children}</WorkspaceShell>
    </SidebarProvider>
  );
}
