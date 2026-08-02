import { renderHook, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AppToastProvider, useToast } from "@/hooks/use-toast";
import { renderWithProviders } from "@/tests/utils/render";

describe("useToast", () => {
  it("shows and dismisses toast notifications", async () => {
    function ToastProbe(): React.JSX.Element {
      const { toast } = useToast();
      return (
        <button
          type="button"
          onClick={() => toast({ title: "Saved", description: "Draft updated." })}
        >
          Notify
        </button>
      );
    }

    const { user } = renderWithProviders(
      <AppToastProvider>
        <ToastProbe />
      </AppToastProvider>,
    );

    await user.click(screen.getByRole("button", { name: "Notify" }));
    expect(await screen.findByText("Saved")).toBeInTheDocument();
    expect(screen.getByText("Draft updated.")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Dismiss notification" }));
    expect(screen.queryByText("Saved")).not.toBeInTheDocument();
  });

  it("replaces an open toast when a new one is requested", async () => {
    function ToastProbe(): React.JSX.Element {
      const { toast } = useToast();
      return (
        <>
          <button type="button" onClick={() => toast({ title: "First" })}>
            First
          </button>
          <button type="button" onClick={() => toast({ title: "Second" })}>
            Second
          </button>
        </>
      );
    }

    const { user } = renderWithProviders(
      <AppToastProvider>
        <ToastProbe />
      </AppToastProvider>,
    );

    await user.click(screen.getByRole("button", { name: "First" }));
    expect(await screen.findByRole("listitem")).toHaveTextContent("First");
    await user.click(screen.getByRole("button", { name: "Second" }));
    expect(await screen.findByRole("listitem")).toHaveTextContent("Second");
    expect(screen.queryByRole("listitem")).toHaveTextContent("Second");
  });

  it("throws when used outside the provider", () => {
    expect(() => renderHook(() => useToast())).toThrow(/AppToastProvider/);
  });
});
