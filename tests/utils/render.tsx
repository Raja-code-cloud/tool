import { render, type RenderOptions, type RenderResult } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import type { ReactElement } from "react";

import { TestProviders, type TestProvidersProps } from "./providers";

export type CustomRenderOptions = Omit<RenderOptions, "wrapper"> &
  Omit<TestProvidersProps, "children">;

export type CustomRenderResult = RenderResult & {
  user: UserEvent;
};

export function renderWithProviders(
  ui: ReactElement,
  options: CustomRenderOptions = {},
): CustomRenderResult {
  const { theme, withSidebar, sidebarCollapsed, ...renderOptions } = options;
  const providerOptions = {
    ...(theme !== undefined ? { theme } : {}),
    ...(withSidebar !== undefined ? { withSidebar } : {}),
    ...(sidebarCollapsed !== undefined ? { sidebarCollapsed } : {}),
  };

  const result = render(ui, {
    wrapper: ({ children }) => <TestProviders {...providerOptions}>{children}</TestProviders>,
    ...renderOptions,
  });

  return { ...result, user: userEvent.setup() };
}
