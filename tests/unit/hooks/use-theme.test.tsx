import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ThemeProvider, useTheme } from "@/components/theme/theme-provider";
import { useTheme as useThemeReexport } from "@/hooks/use-theme";
import { THEME_STORAGE_KEY } from "@/lib/security/constants";

describe("useTheme", () => {
  it("persists theme selection in versioned storage", () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: ({ children }) => (
        <ThemeProvider defaultTheme="dark" storageKey="test-theme">
          {children}
        </ThemeProvider>
      ),
    });

    expect(result.current.resolvedTheme).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);

    act(() => result.current.setTheme("light"));
    expect(result.current.theme).toBe("light");
    expect(result.current.resolvedTheme).toBe("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);

    const stored = window.localStorage.getItem("test-theme");
    expect(stored).toBeTruthy();
    expect(JSON.parse(stored ?? "{}")).toMatchObject({ data: "light" });
  });

  it("migrates legacy plain-string theme values", async () => {
    window.localStorage.setItem(THEME_STORAGE_KEY, "light");

    renderHook(() => useTheme(), {
      wrapper: ({ children }) => (
        <ThemeProvider defaultTheme="dark" storageKey={THEME_STORAGE_KEY}>
          {children}
        </ThemeProvider>
      ),
    });

    await waitFor(() => {
      const migrated = window.localStorage.getItem(THEME_STORAGE_KEY);
      expect(migrated).toBeTruthy();
      expect(JSON.parse(migrated ?? "{}")).toMatchObject({ data: "light" });
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
