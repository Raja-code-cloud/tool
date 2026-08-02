import "@testing-library/jest-dom/vitest";

import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll, beforeEach, expect } from "vitest";
import * as axeMatchers from "vitest-axe/matchers";

import { server } from "../mocks/server";
import { installBrowserMocks } from "./browser";

expect.extend(axeMatchers);

installBrowserMocks();

beforeEach(() => {
  installBrowserMocks();
  Object.defineProperty(navigator, "clipboard", {
    configurable: true,
    value: {
      writeText: async () => undefined,
    },
  });
});

beforeAll(() => {
  server.listen({ onUnhandledRequest: "error" });
});

afterEach(() => {
  cleanup();
  server.resetHandlers();
  window.localStorage.clear();
  document.documentElement.className = "";
  document.documentElement.removeAttribute("style");
});

afterAll(() => {
  server.close();
});
