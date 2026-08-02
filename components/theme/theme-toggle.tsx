"use client";

import { Moon, Sun } from "lucide-react";

import { IconButton } from "@/components/buttons";
import { useTheme } from "@/components/theme/theme-provider";

export type ThemeToggleProps = Omit<React.ComponentProps<typeof IconButton>, "icon" | "label" | "onClick">;

export function ThemeToggle(props: ThemeToggleProps): React.JSX.Element {
  const { resolvedTheme, setTheme } = useTheme();
  const isDark = resolvedTheme === "dark";
  return (
    <IconButton
      label={`Switch to ${isDark ? "light" : "dark"} theme`}
      icon={isDark ? <Sun aria-hidden="true" /> : <Moon aria-hidden="true" />}
      onClick={() => setTheme(isDark ? "light" : "dark")}
      {...props}
    />
  );
}
