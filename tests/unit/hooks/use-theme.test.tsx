import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ThemeProvider, useTheme } from "@/components/theme/theme-provider";
import { useTheme as useThemeReexport } from "@/hooks/use-theme";

describe("useTheme", () => {
  it("persists theme selection in versioned storage", async () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: ({ children }) => (
        <ThemeProvider defaultTheme="dark" storageKey="test-theme">
          {children}
        </ThemeProvider>
      ),
    });

    await waitFor(() => {
      expect(result.current.resolvedTheme).toBe("dark");
    });
    expect(document.documentElement.classList.contains("dark")).toBe(true);

    act(() => result.current.setTheme("light"));

    await waitFor(() => {
      expect(result.current.theme).toBe("light");
      expect(result.current.resolvedTheme).toBe("light");
    });
    expect(document.documentElement.classList.contains("dark")).toBe(false);

    await waitFor(() => {
      const stored = window.localStorage.getItem("test-theme");
      expect(stored).toBeTruthy();
      expect(JSON.parse(stored ?? "{}")).toMatchObject({ data: "light" });
    });
  });

  it("migrates legacy plain-string theme values", async () => {
    const legacyKey = "test-legacy-theme";
    window.localStorage.setItem(legacyKey, "system");

    const { result } = renderHook(() => useTheme(), {
      wrapper: ({ children }) => (
        <ThemeProvider defaultTheme="dark" storageKey={legacyKey}>
          {children}
        </ThemeProvider>
      ),
    });

    await waitFor(() => {
      expect(result.current.theme).toBe("system");
    });

    await waitFor(() => {
      const stored = window.localStorage.getItem(legacyKey);
      expect(stored).toBeTruthy();
      expect(JSON.parse(stored ?? "{}")).toMatchObject({ data: "system" });
    });
  });

  it("re-exports the provider hook from hooks/use-theme", () => {
    const { result } = renderHook(() => useThemeReexport(), {
      wrapper: ({ children }) => (
        <ThemeProvider defaultTheme="dark" storageKey="test-theme-reexport">
          {children}
        </ThemeProvider>
      ),
    });

    expect(result.current.theme).toBe("dark");
  });

  it("throws when used outside the provider", () => {
    expect(() => renderHook(() => useTheme())).toThrow(/ThemeProvider/);
  });
});
