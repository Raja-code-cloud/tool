import { useState } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  Breadcrumbs,
  NotificationButton,
  Pagination,
  Sidebar,
  SidebarMenu,
  SidebarTrigger,
  Tabs,
} from "@/components/navigation/navigation";
import { renderWithProviders, screen } from "@/tests/utils";

const sidebarItems = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Settings", href: "/settings" },
] as const;

describe("navigation components", () => {
  it("renders breadcrumb trail with current page marker", () => {
    renderWithProviders(
      <Breadcrumbs
        items={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Content Library", href: "/content-library" },
          { label: "Azure Guide" },
        ]}
      />,
    );

    expect(screen.getByRole("navigation", { name: "Breadcrumb" })).toBeInTheDocument();
    expect(screen.getByText("Azure Guide")).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute("href", "/dashboard");
  });

  it("changes tabs with keyboard navigation and skips disabled items", async () => {
    function TabsHarness(): React.JSX.Element {
      const [value, setValue] = useState("overview");
      return (
        <>
          <Tabs
            label="Workspace sections"
            value={value}
            onValueChange={setValue}
            items={[
              { id: "overview", label: "Overview" },
              { id: "disabled", label: "Disabled", disabled: true },
              { id: "activity", label: "Activity" },
            ]}
          />
          <div
            role="tabpanel"
            id="panel-overview"
            aria-labelledby="tab-overview"
            hidden={value !== "overview"}
          >
            overview
          </div>
          <div
            role="tabpanel"
            id="panel-activity"
            aria-labelledby="tab-activity"
            hidden={value !== "activity"}
          >
            activity
          </div>
        </>
      );
    }

    const { user } = renderWithProviders(<TabsHarness />);
    const activityTab = screen.getByRole("tab", { name: "Activity" });
    activityTab.focus();
    await user.keyboard("{ArrowLeft}");
    expect(screen.getByRole("tab", { name: "Overview" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("tab", { name: "Disabled" })).toBeDisabled();
  });

  it("paginates results and disables boundary buttons", async () => {
    const onPageChange = vi.fn();
    const { user, rerender } = renderWithProviders(
      <Pagination page={1} pageCount={3} pageSize={10} total={25} onPageChange={onPageChange} />,
    );

    expect(screen.getByText("1–10 of 25")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Previous/i })).toBeDisabled();
    await user.click(screen.getByRole("button", { name: /Next/i }));
    expect(onPageChange).toHaveBeenCalledWith(2);

    rerender(
      <Pagination page={3} pageCount={3} pageSize={10} total={25} onPageChange={onPageChange} />,
    );
    expect(screen.getByRole("button", { name: /Next/i })).toBeDisabled();
  });

  it("opens the mobile sidebar and marks the active route", async () => {
    const { user } = renderWithProviders(
      <>
        <SidebarTrigger />
        <Sidebar items={sidebarItems} currentHref="/dashboard" />
      </>,
      { withSidebar: true },
    );

    expect(screen.getByRole("navigation", { name: "Primary" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Open navigation" }));
    expect(screen.getByRole("button", { name: "Close navigation" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute("aria-current", "page");
  });

  it("announces unread notification counts in the trigger label", () => {
    renderWithProviders(<NotificationButton count={3} />);
    expect(screen.getByRole("button", { name: "Notifications, 3 unread" })).toBeInTheDocument();
  });

  it("renders a primary navigation menu from sidebar items", () => {
    renderWithProviders(<SidebarMenu items={sidebarItems} currentHref="/settings" />);
    expect(screen.getByRole("link", { name: "Settings" })).toHaveAttribute("aria-current", "page");
  });
});
