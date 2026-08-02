import { describe, expect, it } from "vitest";

import { FormErrorSummary } from "@/components/forms/forms";
import { renderWithProviders, screen } from "@/tests/utils";

describe("FormErrorSummary", () => {
  it("lists blocking form errors with alert semantics", () => {
    renderWithProviders(
      <FormErrorSummary
        errors={[
          { id: "project-name", message: "Enter a project name." },
          { id: "category", message: "Select a category." },
        ]}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent("Enter a project name.");
    expect(screen.getByRole("link", { name: "Select a category." })).toBeInTheDocument();
  });

  it("renders nothing when there are no errors", () => {
    renderWithProviders(<FormErrorSummary errors={[]} />);
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
