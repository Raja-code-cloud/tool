import { describe, expect, it, vi } from "vitest";

import { SearchField } from "@/components/forms/search-field";
import { renderWithProviders, screen } from "@/tests/utils";

describe("SearchField", () => {
  it("renders an accessible search input with a custom label", async () => {
    const onChange = vi.fn();
    const { user } = renderWithProviders(
      <SearchField label="Search library" placeholder="Find content" onChange={onChange} />,
    );

    const input = screen.getByRole("searchbox");
    expect(screen.getByText("Search library")).toHaveClass("sr-only");
    await user.type(input, "azure");
    expect(onChange).toHaveBeenCalled();
  });
});
