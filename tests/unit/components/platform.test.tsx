import { describe, expect, it } from "vitest";

import { PlatformBadge, PlatformChip, PlatformIcon } from "@/components/platform/platform";
import { renderWithProviders, screen } from "@/tests/utils";

describe("platform components", () => {
  it("renders platform icons, chips, and badges", () => {
    renderWithProviders(
      <>
        <PlatformIcon platform="linkedin" label="LinkedIn" />
        <PlatformChip platform="linkedin" />
        <PlatformBadge platform="linkedin" />
      </>,
    );

    expect(screen.getByRole("img", { name: "LinkedIn" })).toBeInTheDocument();
    expect(screen.getAllByText("LinkedIn").length).toBeGreaterThan(0);
  });
});
