"use client";

import * as React from "react";

import {
  purgeExpiredClientStorage,
  readVersionedStorage,
  THEME_STORAGE_KEY,
  THEME_STORAGE_TTL_MS,
  writeVersionedStorage,
} from "@/lib/security";

export type Theme = "light" | "dark" | "system";
export type ResolvedTheme = Exclude<Theme, "system">;
export type ThemeContextValue = {
  theme: Theme;
  resolvedTheme: ResolvedTheme;
  setTheme: (theme: Theme) => void;
};
export type ThemeProviderProps = {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
};

const ThemeContext = React.createContext<ThemeContextValue | null>(null);

function isTheme(value: unknown): value is Theme {
  return value === "light" || value === "dark" || value === "system";
}

function resolveTheme(theme: Theme): ResolvedTheme {
  if (theme !== "system") return theme;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(theme: ResolvedTheme): void {
  document.documentElement.classList.toggle("dark", theme === "dark");
  document.documentElement.style.colorScheme = theme;
}

export function ThemeProvider({
  children,
  defaultTheme = "dark",
  storageKey = THEME_STORAGE_KEY,
}: ThemeProviderProps): React.JSX.Element {
  const [theme, setThemeState] = React.useState<Theme>(defaultTheme);
  const [resolvedTheme, setResolvedTheme] = React.useState<ResolvedTheme>(
    defaultTheme === "light" ? "light" : "dark",
  );

  React.useEffect(() => {
    purgeExpiredClientStorage();

    const legacy = window.localStorage.getItem(storageKey);
    if (legacy === "light" || legacy === "dark" || legacy === "system") {
      writeVersionedStorage(storageKey, legacy, THEME_STORAGE_TTL_MS);
      setThemeState(legacy);
      return;
    }

    const stored = readVersionedStorage(storageKey, isTheme);
    const initial = stored.ok ? stored.data : defaultTheme;
    setThemeState(initial);
  }, [defaultTheme, storageKey]);

  React.useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const update = (): void => {
      const next = resolveTheme(theme);
      setResolvedTheme(next);
      applyTheme(next);
    };
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, [theme]);

  const setTheme = React.useCallback(
    (nextTheme: Theme): void => {
      writeVersionedStorage(storageKey, nextTheme, THEME_STORAGE_TTL_MS);
      setThemeState(nextTheme);
    },
    [storageKey],
  );

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const value = React.useContext(ThemeContext);
  if (!value) throw new Error("useTheme must be used within ThemeProvider.");
  return value;
}
