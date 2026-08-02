import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ThemeProvider, useTheme } from "@/components/theme/theme-provider";
import { useTheme as useThemeReexport } from "@/hooks/use-theme";
import { THEME_STORAGE_TTL_MS, writeVersionedStorage } from "@/lib/security";

describe("useTheme", () => {
  it("persists theme selection in localStorage", async () => {
    const storageKey = "test-theme";
    const { result } = renderHook(() => useTheme(), {
      wrapper: ({ children }) => (
        <ThemeProvider defaultTheme="dark" storageKey={storageKey}>
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
      expect(window.localStorage.getItem(storageKey)).toBeTruthy();
    });

    const { result: reloaded } = renderHook(() => useTheme(), {
      wrapper: ({ children }) => (
        <ThemeProvider defaultTheme="dark" storageKey={storageKey}>
          {children}
        </ThemeProvider>
      ),
    });

    await waitFor(() => {
      expect(reloaded.current.theme).toBe("light");
      expect(reloaded.current.resolvedTheme).toBe("light");
    });
  });

  it("reads persisted theme from localStorage on mount", async () => {
    const storageKey = "test-read-theme";
    writeVersionedStorage(storageKey, "system", THEME_STORAGE_TTL_MS);

    const { result } = renderHook(() => useTheme(), {
      wrapper: ({ children }) => (
        <ThemeProvider defaultTheme="dark" storageKey={storageKey}>
          {children}
        </ThemeProvider>
      ),
    });

    await waitFor(() => {
      expect(result.current.theme).toBe("system");
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
