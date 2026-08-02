"use client";

import * as React from "react";

export type UsePaginationOptions = { initialPage?: number; pageCount: number };
export type PaginationState = {
  page: number;
  pageCount: number;
  canGoPrevious: boolean;
  canGoNext: boolean;
  setPage: (page: number) => void;
  nextPage: () => void;
  previousPage: () => void;
};

export function usePagination({
  initialPage = 1,
  pageCount,
}: UsePaginationOptions): PaginationState {
  const safePageCount = Math.max(1, Math.floor(pageCount));
  const [page, setPageState] = React.useState(() =>
    Math.min(safePageCount, Math.max(1, Math.floor(initialPage))),
  );
  const setPage = React.useCallback(
    (nextPage: number): void => {
      setPageState(Math.min(safePageCount, Math.max(1, Math.floor(nextPage))));
    },
    [safePageCount],
  );
  React.useEffect(() => setPage(page), [page, setPage]);
  return {
    page,
    pageCount: safePageCount,
    canGoPrevious: page > 1,
    canGoNext: page < safePageCount,
    setPage,
    nextPage: () => setPage(page + 1),
    previousPage: () => setPage(page - 1),
  };
}
