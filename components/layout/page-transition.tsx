"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

export type PageTransitionProps = { children: ReactNode };

/**
 * Fades and lifts route content on navigation.
 *
 * Implemented as a CSS animation rather than a motion library: keying the
 * wrapper on the pathname remounts it, which replays the animation for the
 * cost of one class. Reduced-motion is handled globally in `globals.css`.
 */
export function PageTransition({ children }: PageTransitionProps): React.JSX.Element {
  const pathname = usePathname();

  return (
    <div key={pathname} className="page-enter">
      {children}
    </div>
  );
}
