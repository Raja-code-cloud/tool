import { describe, expect, it } from "vitest";

import {
  Card,
  CardHeader,
  InteractiveCard,
  MetricCard,
  UploadCard,
} from "@/components/cards/cards";
import { renderWithProviders, screen } from "@/tests/utils";

describe("card components", () => {
  it("renders metric cards with comparison text", () => {
    renderWithProviders(
      <MetricCard label="Scheduled posts" value="24" trend="up" comparison="+12% vs last week" />,
    );

    expect(screen.getByText("Scheduled posts")).toBeInTheDocument();
    expect(screen.getByText("24")).toBeInTheDocument();
    expect(screen.getByText(/\+12% vs last week/)).toBeInTheDocument();
  });

  it("renders card headers with configurable heading levels and ids", () => {
    renderWithProviders(
      <CardHeader
        title="Workspace"
        description="Overview metrics"
        headingLevel={2}
        headingId="workspace-heading"
      />,
    );

    expect(screen.getByRole("heading", { level: 2, name: "Workspace" })).toHaveAttribute(
      "id",
      "workspace-heading",
    );
    expect(screen.getByText("Overview metrics")).toBeInTheDocument();
  });

  it("renders interactive cards as navigable articles", () => {
    renderWithProviders(
      <InteractiveCard href="/settings" title="Open settings">
        Manage workspace defaults
      </InteractiveCard>,
    );

    expect(screen.getByRole("article")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Open settings/i })).toHaveAttribute(
      "href",
      "/settings",
    );
    expect(screen.getByText("Manage workspace defaults")).toBeInTheDocument();
  });

  it("supports semantic card containers and dashed upload styling", () => {
    renderWithProviders(
      <>
        <Card as="section" aria-label="Metrics">
          Metrics body
        </Card>
        <UploadCard>Drop files here</UploadCard>
      </>,
    );

    expect(screen.getByRole("region", { name: "Metrics" })).toHaveTextContent("Metrics body");
    expect(screen.getByText("Drop files here").closest(".border-dashed")).toBeTruthy();
  });
});
