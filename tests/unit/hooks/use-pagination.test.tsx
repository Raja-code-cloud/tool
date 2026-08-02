import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { usePagination } from "@/hooks/use-pagination";

describe("usePagination", () => {
  it("clamps page changes within bounds", () => {
    const { result } = renderHook(() => usePagination({ pageCount: 5, initialPage: 3 }));

    expect(result.current.page).toBe(3);
    expect(result.current.canGoPrevious).toBe(true);
    expect(result.current.canGoNext).toBe(true);

    act(() => result.current.setPage(99));
    expect(result.current.page).toBe(5);

    act(() => result.current.setPage(0));
    expect(result.current.page).toBe(1);
  });

  it("navigates with next and previous helpers", () => {
    const { result } = renderHook(() => usePagination({ pageCount: 3, initialPage: 2 }));

    act(() => result.current.nextPage());
    expect(result.current.page).toBe(3);
    expect(result.current.canGoNext).toBe(false);

    act(() => result.current.previousPage());
    expect(result.current.page).toBe(2);
    expect(result.current.canGoPrevious).toBe(true);
  });

  it("normalizes invalid page counts and initial pages", () => {
    const { result } = renderHook(() => usePagination({ pageCount: 0, initialPage: -5 }));
    expect(result.current.pageCount).toBe(1);
    expect(result.current.page).toBe(1);
    expect(result.current.canGoNext).toBe(false);
  });
});
