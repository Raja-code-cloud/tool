import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SidebarProvider, useSidebar } from "@/hooks/use-sidebar";

describe("useSidebar", () => {
  it("opens, closes, and toggles the mobile drawer", () => {
    const { result } = renderHook(() => useSidebar(), {
      wrapper: ({ children }) => <SidebarProvider>{children}</SidebarProvider>,
    });

    expect(result.current.isOpen).toBe(false);
    act(() => result.current.open());
    expect(result.current.isOpen).toBe(true);
    act(() => result.current.close());
    expect(result.current.isOpen).toBe(false);
    act(() => result.current.toggle());
    expect(result.current.isOpen).toBe(true);
  });

  it("toggles collapsed desktop state", () => {
    const { result } = renderHook(() => useSidebar(), {
      wrapper: ({ children }) => (
        <SidebarProvider defaultCollapsed={false}>{children}</SidebarProvider>
      ),
    });

    expect(result.current.isCollapsed).toBe(false);
    act(() => result.current.toggleCollapsed());
    expect(result.current.isCollapsed).toBe(true);
    act(() => result.current.toggleCollapsed());
    expect(result.current.isCollapsed).toBe(false);
  });

  it("throws when used outside the provider", () => {
    expect(() => renderHook(() => useSidebar())).toThrow(/SidebarProvider/);
  });
});
