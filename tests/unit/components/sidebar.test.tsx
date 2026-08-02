import { describe, expect, it } from "vitest";

import { Sidebar, SidebarMenu } from "@/components/navigation/navigation";
import { ROUTES } from "@/constants/navigation";
import { renderWithProviders, screen } from "@/tests/utils";

describe("sidebar navigation", () => {
  const items = [
    { label: "Dashboard", href: ROUTES.dashboard },
    { label: "Content Library", href: ROUTES.contentLibrary },
  ];

  it("marks the active route in the primary menu", () => {
    renderWithProviders(<SidebarMenu items={items} currentHref={ROUTES.dashboard} />, {
      withSidebar: true,
    });

    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Content Library" })).not.toHaveAttribute(
      "aria-current",
    );
  });

  it("renders the mobile sidebar shell", () => {
    renderWithProviders(
      <Sidebar items={items} currentHref={ROUTES.dashboard} header="Workspace" />,
      {
        withSidebar: true,
      },
    );

    expect(screen.getByText("Workspace")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Primary" })).toBeInTheDocument();
  });
});
