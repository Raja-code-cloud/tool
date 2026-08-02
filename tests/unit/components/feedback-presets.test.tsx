import { describe, expect, it } from "vitest";

import {
  LiveRegion,
  LoadingOverlay,
  NoData,
  NoResults,
  SkeletonCard,
  SkeletonTable,
  SkeletonText,
} from "@/components/feedback/feedback";
import { renderWithProviders, screen } from "@/tests/utils";

describe("feedback composition components", () => {
  it("renders empty-state presets", () => {
    renderWithProviders(
      <>
        <NoResults title="No matches" description="Try another query." />
        <NoData title="No analytics yet" description="Publish content to populate this view." />
      </>,
    );

    expect(screen.getByText("No matches")).toBeInTheDocument();
    expect(screen.getByText("No analytics yet")).toBeInTheDocument();
  });

  it("renders skeleton and live region helpers", () => {
    renderWithProviders(
      <>
        <SkeletonText lines={2} />
        <SkeletonCard hasMedia />
        <SkeletonTable rows={2} columns={2} />
        <LiveRegion politeness="assertive">Saved</LiveRegion>
        <LoadingOverlay label="Refreshing library" />
      </>,
    );

    expect(screen.getByText("Saved")).toBeInTheDocument();
    expect(screen.getByText("Refreshing library")).toBeInTheDocument();
  });
});
