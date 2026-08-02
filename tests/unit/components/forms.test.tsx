import { describe, expect, it } from "vitest";

import { CharacterCount, FormErrorSummary, FormField } from "@/components/forms/forms";
import { Input } from "@/components/ui";
import { renderWithProviders, screen } from "@/tests/utils";

describe("form components", () => {
  it("associates labels, descriptions, and errors with inputs", () => {
    renderWithProviders(
      <FormField
        id="project-name"
        label="Project name"
        isRequired
        description="Visible in the content library."
        error="Enter a project name."
      >
        <Input defaultValue="" />
      </FormField>,
    );

    const input = screen.getByLabelText(/Project name/);
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(input).toHaveAttribute("aria-required", "true");
    expect(input).toHaveAttribute(
      "aria-describedby",
      "project-name-description project-name-error",
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Enter a project name.");
  });

  it("warns when character count nears or exceeds the limit", () => {
    const { rerender } = renderWithProviders(<CharacterCount current={900} maximum={1000} />);
    expect(screen.getByText("900/1000")).toHaveClass("text-warning");

    rerender(<CharacterCount current={1000} maximum={1000} />);
    expect(screen.getByText("1000/1000")).toHaveClass("text-destructive");
  });

  it("summarizes form errors with in-page links", () => {
    renderWithProviders(
      <FormErrorSummary
        errors={[
          { id: "email", message: "Email is required" },
          { id: "title", message: "Title is required" },
        ]}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent("Please fix the following");
    expect(screen.getByRole("link", { name: "Email is required" })).toHaveAttribute(
      "href",
      "#email",
    );
  });

  it("renders nothing when the error summary has no errors", () => {
    renderWithProviders(<FormErrorSummary errors={[]} />);
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
