import { describe, expect, it } from "vitest";

import { ThemeToggle } from "@/components/theme/theme-toggle";
import { renderWithProviders, screen } from "@/tests/utils";

describe("ThemeToggle", () => {
  it("toggles between light and dark themes", async () => {
    const { user } = renderWithProviders(<ThemeToggle />, { theme: "dark" });

    const lightToggle = screen.getByRole("button", { name: "Switch to light theme" });
    expect(document.documentElement.classList.contains("dark")).toBe(true);

    await user.click(lightToggle);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(screen.getByRole("button", { name: "Switch to dark theme" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Switch to dark theme" }));
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("persists the selected theme through the provider", async () => {
    const { user } = renderWithProviders(<ThemeToggle />, { theme: "light" });

    await user.click(screen.getByRole("button", { name: "Switch to dark theme" }));
    const stored = window.localStorage.getItem("test-theme");
    expect(stored).toBeTruthy();
    expect(JSON.parse(stored ?? "{}")).toMatchObject({ data: "dark" });
  });
});
