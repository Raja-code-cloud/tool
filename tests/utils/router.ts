import { vi } from "vitest";

export type RouterMock = {
  back: ReturnType<typeof vi.fn>;
  forward: ReturnType<typeof vi.fn>;
  prefetch: ReturnType<typeof vi.fn>;
  push: ReturnType<typeof vi.fn>;
  refresh: ReturnType<typeof vi.fn>;
  replace: ReturnType<typeof vi.fn>;
};

export function createRouterMock(): RouterMock {
  return {
    back: vi.fn(),
    forward: vi.fn(),
    prefetch: vi.fn().mockResolvedValue(undefined),
    push: vi.fn(),
    refresh: vi.fn(),
    replace: vi.fn(),
  };
}

export function mockNextNavigation(pathname = "/"): RouterMock {
  const router = createRouterMock();

  vi.doMock("next/navigation", () => ({
    redirect: vi.fn(),
    useParams: vi.fn(() => ({})),
    usePathname: vi.fn(() => pathname),
    useRouter: vi.fn(() => router),
    useSearchParams: vi.fn(() => new URLSearchParams()),
  }));

  return router;
}
