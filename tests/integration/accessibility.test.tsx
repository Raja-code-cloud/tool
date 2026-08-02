import { useState } from "react";
import { describe, expect, it } from "vitest";

import { PrimaryButton } from "@/components/buttons";
import { SearchField } from "@/components/forms/search-field";
import { Breadcrumbs, Tabs } from "@/components/navigation/navigation";
import { expectNoCriticalViolations, renderWithProviders, screen } from "@/tests/utils";

function TabsWithPanels(): React.JSX.Element {
  const [value, setValue] = useState("upload");
  return (
    <>
      <Tabs
        label="Sections"
        value={value}
        onValueChange={setValue}
        items={[
          { id: "upload", label: "Upload" },
          { id: "review", label: "Review" },
        ]}
      />
      <div
        role="tabpanel"
        id="panel-upload"
        aria-labelledby="tab-upload"
        hidden={value !== "upload"}
      >
        Upload step
      </div>
      <div
        role="tabpanel"
        id="panel-review"
        aria-labelledby="tab-review"
        hidden={value !== "review"}
      >
        Review step
      </div>
    </>
  );
}

describe("accessibility integration", () => {
  it("has no critical axe violations in breadcrumbs, search, and tabbed panels", async () => {
    const { container } = renderWithProviders(
      <>
        <Breadcrumbs
          items={[{ label: "Dashboard", href: "/dashboard" }, { label: "Upload Wizard" }]}
        />
        <SearchField label="Search content" placeholder="Search" />
        <TabsWithPanels />
        <PrimaryButton>Continue</PrimaryButton>
      </>,
    );

    expect(screen.getByRole("navigation", { name: "Breadcrumb" })).toBeInTheDocument();
    expect(screen.getByRole("searchbox")).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Upload" })).toHaveAttribute(
      "aria-controls",
      "panel-upload",
    );
    await expectNoCriticalViolations(container);
  });
});
