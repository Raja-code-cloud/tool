import { withThemeByClassName } from "@storybook/addon-themes";
import type { Decorator, Preview } from "@storybook/react";
import * as React from "react";

import { ThemeProvider, useTheme } from "../components/theme/theme-provider";
import { ToastProvider } from "../components/ui";
import { SidebarProvider } from "../hooks/use-sidebar";

import "../styles/globals.css";

function ThemeBridge({ theme }: { theme: "light" | "dark" }): null {
  const { setTheme } = useTheme();
  React.useEffect(() => setTheme(theme), [setTheme, theme]);
  return null;
}

const withAppProviders: Decorator = (Story, context) => {
  const theme = context.globals.theme === "dark" ? "dark" : "light";
  return (
    <ThemeProvider defaultTheme={theme} storageKey="storybook-theme">
      <ThemeBridge theme={theme} />
      <SidebarProvider>
        <ToastProvider>
          <div className="bg-background text-foreground tablet:p-6 min-h-screen p-4">
            <Story />
          </div>
        </ToastProvider>
      </SidebarProvider>
    </ThemeProvider>
  );
};

const preview: Preview = {
  decorators: [
    withAppProviders,
    withThemeByClassName({
      themes: { light: "", dark: "dark" },
      defaultTheme: "light",
    }),
  ],
  parameters: {
    actions: { argTypesRegex: "^on[A-Z].*" },
    backgrounds: {
      options: {
        app: { name: "App", value: "var(--background)" },
        light: { name: "Light", value: "#f7f8fa" },
        dark: { name: "Dark", value: "#090b0f" },
      },
    },
    controls: { expanded: true, sort: "requiredFirst" },
    docs: {
      canvas: { sourceState: "shown" },
      description: {
        component:
          "Responsive in mobile, tablet, and desktop viewports. Verify keyboard operation, visible focus, semantic labels, and light/dark contrast.",
      },
    },
    options: {
      storySort: {
        order: [
          "Foundations",
          "Components",
          "Forms",
          "Navigation",
          "Feedback",
          "Data Display",
          "Charts",
          "Layouts",
          "Upload",
          "Platform",
          "Utilities",
        ],
      },
    },
    viewport: {
      options: {
        mobile: { name: "Mobile", styles: { width: "375px", height: "812px" } },
        tablet: { name: "Tablet", styles: { width: "768px", height: "1024px" } },
        desktop: { name: "Desktop", styles: { width: "1440px", height: "900px" } },
      },
    },
  },
  initialGlobals: {
    backgrounds: { value: "app" },
    theme: "light",
    viewport: { value: "desktop", isRotated: false },
  },
  tags: ["autodocs"],
};

export default preview;
