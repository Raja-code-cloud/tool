import { describe, expect, it, vi } from "vitest";

import {
  ActionButton,
  CopyButton,
  DestructiveButton,
  IconButton,
  OutlineButton,
  PrimaryButton,
  SecondaryButton,
} from "@/components/buttons";
import { renderWithProviders, screen } from "@/tests/utils";

describe("button components", () => {
  it("renders variant buttons and forwards click handlers", async () => {
    const onClick = vi.fn();
    const { user } = renderWithProviders(
      <>
        <PrimaryButton onClick={onClick}>Save draft</PrimaryButton>
        <SecondaryButton>Cancel</SecondaryButton>
        <OutlineButton>Preview</OutlineButton>
        <DestructiveButton>Delete</DestructiveButton>
      </>,
    );

    await user.click(screen.getByRole("button", { name: "Save draft" }));
    expect(onClick).toHaveBeenCalledOnce();
    expect(screen.getByRole("button", { name: "Delete" })).toBeInTheDocument();
  });

  it("renders icon and action buttons with accessible labels", () => {
    renderWithProviders(
      <>
        <IconButton label="Open filters" icon={<span data-testid="filter-icon" />} />
        <ActionButton leadingIcon={<span data-testid="leading-icon" />}>Continue</ActionButton>
      </>,
    );

    expect(screen.getByRole("button", { name: "Open filters" })).toHaveAttribute(
      "title",
      "Open filters",
    );
    expect(screen.getByRole("button", { name: "Continue" })).toBeInTheDocument();
    expect(screen.getByTestId("leading-icon").parentElement).toHaveAttribute("aria-hidden", "true");
  });

  it("copies text to the clipboard and shows confirmation state", async () => {
    const onCopied = vi.fn();
    const { user } = renderWithProviders(
      <CopyButton value="hello-world" label="Copy snippet" onCopied={onCopied} />,
    );

    await user.click(screen.getByRole("button", { name: "Copy snippet" }));
    expect(await screen.findByRole("button", { name: "Copied" })).toBeInTheDocument();
    expect(onCopied).toHaveBeenCalledOnce();
  });
});
